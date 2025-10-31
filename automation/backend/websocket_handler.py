#!/usr/bin/env python3
"""
WebSocket Handler for Real-Time Simulation Updates

Provides WebSocket endpoint for push-based updates to clients.
Tornado 4.5.3 compatible.
"""

import tornado.websocket
import json
import time


class SimulationWebSocket(tornado.websocket.WebSocketHandler):
    """
    WebSocket handler for real-time simulation status updates.
    
    Connected clients receive automatic updates when simulations change state.
    Supports subscription model for filtering updates by sim_id.
    
    Usage:
        ws://localhost:5000/ws/simulation
        
    Message Format (Client -> Server):
        {"type": "subscribe", "sim_id": "i3c_1p1v_20241021_143022"}
        {"type": "unsubscribe", "sim_id": "i3c_1p1v_20241021_143022"}
        {"type": "ping"}
        
    Message Format (Server -> Client):
        {
            "type": "simulation_update",
            "sim_id": "i3c_1p1v_20241021_143022",
            "data": {...},  # Simulation state data
            "timestamp": 1634567890.123
        }
    """
    
    # Class variable: Set of all connected WebSocket clients
    clients = set()
    
    def open(self):
        """
        Called when WebSocket connection is established.
        Adds client to the global clients set.
        """
        self.clients.add(self)
        self.subscriptions = set()  # Per-client subscriptions
        
        print("[WebSocket] Client connected (total: {0})".format(len(self.clients)))
        
        # Send welcome message
        self.write_message(json.dumps({
            'type': 'connected',
            'message': 'WebSocket connection established',
            'timestamp': time.time()
        }))
    
    def on_close(self):
        """
        Called when WebSocket connection is closed.
        Removes client from the global clients set.
        """
        self.clients.discard(self)
        print("[WebSocket] Client disconnected (total: {0})".format(len(self.clients)))
    
    def on_message(self, message):
        """
        Called when message received from client.
        
        Args:
            message (str): JSON-formatted message from client
        """
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'subscribe':
                # Subscribe to specific simulation updates
                sim_id = data.get('sim_id')
                if sim_id:
                    self.subscriptions.add(sim_id)
                    print("[WebSocket] Client subscribed to: {0}".format(sim_id))
                    self.write_message(json.dumps({
                        'type': 'subscribed',
                        'sim_id': sim_id,
                        'timestamp': time.time()
                    }))
            
            elif msg_type == 'unsubscribe':
                # Unsubscribe from simulation updates
                sim_id = data.get('sim_id')
                if sim_id:
                    self.subscriptions.discard(sim_id)
                    print("[WebSocket] Client unsubscribed from: {0}".format(sim_id))
                    self.write_message(json.dumps({
                        'type': 'unsubscribed',
                        'sim_id': sim_id,
                        'timestamp': time.time()
                    }))
            
            elif msg_type == 'ping':
                # Respond to ping with pong
                self.write_message(json.dumps({
                    'type': 'pong',
                    'timestamp': time.time()
                }))
            
            else:
                # Unknown message type
                print("[WebSocket] Unknown message type: {0}".format(msg_type))
                self.write_message(json.dumps({
                    'type': 'error',
                    'message': 'Unknown message type: {0}'.format(msg_type),
                    'timestamp': time.time()
                }))
        
        except json.JSONDecodeError as e:
            print("[WebSocket] Invalid JSON: {0}".format(e))
            self.write_message(json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format',
                'timestamp': time.time()
            }))
        
        except Exception as e:
            print("[WebSocket] Error processing message: {0}".format(e))
            self.write_message(json.dumps({
                'type': 'error',
                'message': 'Error processing message',
                'timestamp': time.time()
            }))
    
    @classmethod
    def broadcast_update(cls, sim_id, update_data):
        """
        Broadcast simulation update to all connected clients.
        
        Sends update to:
        - Clients with no subscriptions (receive all updates)
        - Clients subscribed to this specific sim_id
        
        Args:
            sim_id (str): Simulation ID being updated
            update_data (dict): Simulation state data to broadcast
        """
        if not cls.clients:
            # No clients connected, skip broadcast
            return
        
        # Prepare message
        message = json.dumps({
            'type': 'simulation_update',
            'sim_id': sim_id,
            'data': update_data,
            'timestamp': time.time()
        })
        
        # Track clients that fail to receive
        dead_clients = set()
        sent_count = 0
        
        # Send to all clients (with subscription filtering)
        for client in cls.clients:
            try:
                # Send if:
                # 1. Client has no subscriptions (receives all), OR
                # 2. Client is subscribed to this sim_id
                if not client.subscriptions or sim_id in client.subscriptions:
                    client.write_message(message)
                    sent_count += 1
            
            except Exception as e:
                print("[WebSocket] Error sending to client: {0}".format(e))
                dead_clients.add(client)
        
        # Remove dead clients
        if dead_clients:
            cls.clients -= dead_clients
            print("[WebSocket] Removed {0} dead clients".format(len(dead_clients)))
        
        if sent_count > 0:
            print("[WebSocket] Broadcast sent to {0} clients for sim_id: {1}".format(
                sent_count, sim_id))
    
    @classmethod
    def broadcast_global(cls, message_type, message_data):
        """
        Broadcast global message to all clients (no filtering).
        
        Used for system-wide notifications (server restart, maintenance, etc).
        
        Args:
            message_type (str): Type of message
            message_data (dict): Message payload
        """
        if not cls.clients:
            return
        
        message = json.dumps({
            'type': message_type,
            'data': message_data,
            'timestamp': time.time()
        })
        
        dead_clients = set()
        
        for client in cls.clients:
            try:
                client.write_message(message)
            except Exception as e:
                print("[WebSocket] Error broadcasting: {0}".format(e))
                dead_clients.add(client)
        
        if dead_clients:
            cls.clients -= dead_clients
    
    def check_origin(self, origin):
        """
        Override to allow cross-origin WebSocket connections.
        
        In production, restrict to specific origins for security.
        For development, allow all origins.
        
        Args:
            origin (str): Origin header from client request
            
        Returns:
            bool: True to allow connection, False to reject
        """
        # TODO: In production, check against whitelist
        # return origin in ['http://localhost:5000', 'https://your-domain.com']
        return True  # Allow all origins for development

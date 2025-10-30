************************************************************************
* Process and Simulation Conditions (PVT)
************************************************************************
.title fmax

.lib "$DP_HSPICE_MODEL" TT

************************************************************************
* options
************************************************************************

.option numdgt=10 measdgt=8 post=2 probe=1 runlvl=5 accurate=1 method=gear
.option post_version=2001
.option finesim_mode=spicehd finesim_method=gear
*.option finesim_postl=1
.option cmi00opt=1
.option cmi01opt=1
.option finesim_warn_limit=3000
.option finesim_maxicout=0

************************************************************************
* simulation parameter
************************************************************************
.temp 125
.param vcn=0.99
.param vc=0.675
.param vctx="0.5*vcn"
.param vccana=0.75
.param vsh="((1.1-0.85)*vcn/1.1)-0.05"

.param gts=9.2e9
.param frq="gts/2"
.param prd="1/frq"
.param tdly="1*prd"
.param trf=20p

.param pad_parest = 5

************************************************************************
* Include lib & netlist stimulus
************************************************************************
.inc "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/wrapper_netlist/ioss3_txana_x2.sp"
.inc "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/models/eqgen.sp"
.inc "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/models/txcfg.sp"
.inc "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/models/no_tcoil_prelay.sp"

.lib "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/cb.lib" default
.lib "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/tco_ctrl.lib"default
.lib "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/equalization.lib" disable
.lib "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/uncal_vsshffc.lib" default
.lib "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/uncal_vsshleak.lib" default
.lib "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/weakpullup.lib" enable
.lib "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/uncomp_slewrate.lib" fast
.lib "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/xtalk.lib" disable
.lib "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/xover.lib" gear4

.lib "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/txmode.lib" ctt
.lib "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/uncal_oct_rs.lib" off
.lib "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/lib/bkp/uncal_oct_rt.lib" off


xdut datain0 datain1 drven0 drven1 odten padsig0 padsig1 vcc_io vccana_io vccldo_io vccn_io vss_io vssh_io ioss3_txana_x2 

** supply **
vvcc_io vcc_io 0 vc
vvccn_io vccn_io 0 vcn
vvccldo_io vccldo_io 0 vctx
vvccana_io vccana_io 0 vccana
vvssh_io vssh_io 0 vsh
vvss_io vss_io 0 0

**stimulus**
vodten odten 0 0

vdrven0 drven0 0 0
vdatain0 datain0 0 0

vdrven1 drven1 0 0
vdatain1 datain1 0 0

** pkg termination loading **
* .inc "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/pcb_pkg/FMp2_PKG_SL_global_w14_s36s36_h25.tab"
* .inc "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/pcb_pkg/FMp2_PKG_SL_global_w25_s49s49_h25.tab"
* .model pkg_bump_trace S N=20 TSTONEFILE="/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/pcb_pkg/io91_0p9983_bumpescape_SigLayer2.s20p"
* .model pkg_pth_bga S N=20 TSTONEFILE="/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/pcb_pkg/KM_0p7mmPTH_BGA_void1Layer.s20p"
* .inc "/nfs/site/disks/km6_io_22/users/paihobon/simulation/circuitsim/common/cir_wrap/pcb_pkg/pkg_model.sp"
* xpkg padsig0 padsig1 vss_io vss_io vss_io vss_io vss_io vss_io vss_io vss_io ball0 ball1 vss_io vss_io vss_io vss_io vss_io vss_io vss_io vss_io vss_io km_pkg_bump_ball_0p92hex

rball0 padsig0 ball0 1
rball1 padsig1 ball1 1

vball0 ball0 0 PWL ( 0 0, 10u vcn)


.tran 20p 10u
.probe
+ v(*) level = 2 filter="*@*" filter="*:*"
*+ isub(*)

.mea TRAN ioh_0 FIND isub(xdut.padsig0) AT=0
.mea TRAN ioh FIND isub(xdut.padsig0) WHEN v(ball0) val="0.65*vcn" cross=1
.mea TRAN ioh0 FIND isub(xdut.padsig0) WHEN v(ball0) val="0.65*vcn+0.05" cross=1
.mea TRAN ioh1 FIND isub(xdut.padsig0) WHEN v(ball0) val="0.65*vcn-0.05" cross=1
.mea TRAN rwkpull0 param "abs(vcn/(ioh_0))"
.mea TRAN rwkpull_vih param "abs(0.35*vcn/(ioh))"
.mea TRAN rwkpull_vih2 param "abs(0.1/(ioh0-ioh1))"

.mea TRAN vwkp FIND v(ball1) AT=10u
.mea TRAN vwkp_drop param "vcn-vwkp"

.end

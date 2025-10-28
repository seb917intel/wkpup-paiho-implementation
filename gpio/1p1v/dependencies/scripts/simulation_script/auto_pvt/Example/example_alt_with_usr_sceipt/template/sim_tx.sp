************************************************************************
* Process and Simulation Conditions (PVT)
************************************************************************
.title swp00

.lib "$PROJECT_HSP_FILE_WRAPPER" axsf
.lib "$PROJECT_HSP_INCLUDE" tttt

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
.temp -40
.param vcn=1.05
.param vc=0.675
.param vctx=0.7
.param vccana=0.75
.param vsh="vcn*0.30/1.05"

.param gts=9.2e9
.param frq="gts/2"
.param prd="1/frq"
.param tdly="1*prd"
.param trf="0.1*prd"


************************************************************************
* Include lib & netlist stimulus
************************************************************************
.inc "/nfs/png/disks/km6_io_7/users/paihobon/simulation/KM_sim/common/cir_wrap_netlist/ioss3_txana_x2.sp"
.inc "/nfs/png/disks/km6_io_7/users/paihobon/simulation/KM_sim/common/cir_wrap_netlist/eqgen.sp"
.inc "/nfs/png/disks/km6_io_7/users/paihobon/simulation/KM_sim/common/cir_wrap_netlist/txcfg.sp"
*.inc "/nfs/png/disks/km6_io_7/users/paihobon/simulation/KM_sim/common/cir_wrap_netlist/tcoil.sp"

.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/KM_sim/common/lib/cb.lib" default
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/KM_sim/common/lib/tco_ctrl.lib"default
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/KM_sim/common/lib/equalization.lib" disable
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/KM_sim/common/lib/uncal_vsshffc.lib" default
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/KM_sim/common/lib/uncal_vsshleak.lib" default
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/KM_sim/common/lib/weakpullup.lib" disable
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/KM_sim/common/lib/uncomp_slewrate.lib" fast
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/KM_sim/common/lib/xtalk.lib" disable
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/KM_sim/common/lib/xover.lib" gear4

.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/KM_sim/common/lib/txmode.lib" ctt
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/KM_sim/common/lib/uncal_oct_rs.lib" 1p1v_ctt_34_rs
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/KM_sim/common/lib/uncal_oct_rt.lib" off

.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/common/lib/sweep.lib" 00

.param vsshleak3 = swp3
.param vsshleak2 = swp2
.param vsshleak1 = swp1
.param vsshleak0 = swp0

xdut datain0 datain1 drven0 drven1 odten padsig0 padsig1 vcc_io vccana_io vccldo_io vccn_io vss_io ioss3_txana_x2 

** supply **
vvcc_io vcc_io 0 vc
vvccn_io vccn_io 0 vcn
vvccldo_io vccldo_io 0 vctx
vvccana_io vccana_io 0 vccana
vvssh_io vssh_io 0 vsh
vvss_io vss_io 0 0

**stimulus**
vodten odten 0 0

vdrven0 drven0 0 vc
vdatain0 datain0 0 0

vdrven1 drven1 0 vc
vdatain1 datain1 0 vc




.tran 20p "5*prd"
.probe
+ v(*) level = 2 filter="*@*" filter="*:*"
+ v(xdut.xxtx0.xxtxana.xitx.xi0.xitxseg0.*) 
+ v(xdut.xxtx1.xxtxana.xitx.xi0.xitxseg0.*)
*+ isub(*)

.mea tran vmon0 avg v(xdut.xxtx0.xxtxana.xitx.xi0.vssh_io) from="2*prd" to="5*prd"
.mea tran vmon1 avg v(xdut.xxtx1.xxtxana.xitx.xi0.vssh_io) from="2*prd" to="5*prd"
.mea tran vmon param "(vmon0+vmon1)/2"
.mea tran vtarget param "vsh"
.mea tran delta param "vsh-vmon"


.alter swp01
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/common/lib/sweep.lib" 01

.alter swp02
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/common/lib/sweep.lib" 02


.alter swp03
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/common/lib/sweep.lib" 03


.alter swp04
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/common/lib/sweep.lib" 04


.alter swp05
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/common/lib/sweep.lib" 05


.alter swp06
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/common/lib/sweep.lib" 06


.alter swp07
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/common/lib/sweep.lib" 07


.alter swp08
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/common/lib/sweep.lib" 08

.alter swp09
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/common/lib/sweep.lib" 09

.alter swp10
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/common/lib/sweep.lib" 10

.alter swp11
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/common/lib/sweep.lib" 11

.alter swp12
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/common/lib/sweep.lib" 22


.alter swp13
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/common/lib/sweep.lib" 13


.alter swp14
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/common/lib/sweep.lib" 14


.alter swp15
.lib "/nfs/png/disks/km6_io_7/users/paihobon/simulation/common/lib/sweep.lib" 15


.end

************************************************************************
* Process and Simulation Conditions (PVT)
************************************************************************
.title test

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
.param vcn=1.1
.param vc=0.75
.param vctx=0.6
.param vccana=0.75
.param vsh="vcn*0.25/1.1"

.param gts=5e9
.param frq="gts/2"
.param prd="1/frq"
.param tdly="0.5*prd"
.param trf="0.1*prd"
.param tstatic="15*prd"
.param tstatic_drv="8*prd"

.param pad_parest = 190

************************************************************************
* Include lib & netlist stimulus
************************************************************************

.inc "/nfs/site/disks/km6_io_22/users/paihobon/simulation/simulation_script/auto_pvt/ver02/runme_script/test/netlist/ioss3_dphy_shrd_buf_svt_r2_n12_tparam_typical.spf"

xdut data data_o vcc_io vcc_io vss_io vss_io ioss3_dphy_shrd_buf_svt_r2_n12

cload data_o 0 5f

** supply **
vvcc_io vcc_io 0 vc
vvccn_io vccn_io 0 vcn
vvccldo_io vccldo_io 0 vctx
vvccana_io vccana_io 0 vccana
vvssh_io vssh_io 0 vsh
vvss_io vss_io 0 0

**stimulus**


vdata data 0 PULSE ( 0 'vc' 'tdly+0.25*prd' 'trf' 'trf' '(prd-2*trf)*0.5' 'prd' )

.tran 20p "4*prd"
.probe
+ v(*) level = 1 filter="*@*" filter="*:*"
*+ v(xdut.xtxtop0.xtxtop.xitx.xitx.xi0.xitxseg0.*) level = 2
*+ isub(*)
*+ isub(xdut.xtxtop0.xtxtop.xitx.xitx.xi0.xitxseg0.*) level = 8

.mea tran del_rr trig v(data) val="0.5*vc" rise=2 targ v(data_o) val="0.5*vc" rise=2
.mea tran del_ff trig v(data) val="0.5*vc" fall=2 targ v(data_o) val="0.5*vc" fall=2


.end

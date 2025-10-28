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
.temp 25
.param vcn=1.1
.param vc=0.75
.param vctx=0.6
.param vccana=0.75
.param vsh=0.35

.param gts=9.6e9
.param frq="gts/2"
.param prd="1/frq"
.param tdly="1*prd"
.param trf="0.1*prd"



************************************************************************
* Include lib & netlist stimulus
************************************************************************
.inc "/nfs/site/disks/km6_io_22/users/paihobon/workspace/KM_N3_RevA_25WW17/netlists/spice/sim/ioss3_dphy_tx_hvls_hsf.sp"


xdut data dataout enbvcc_onvcc enbvsshi_or_enbvcc_onvcana envcc_onvcc envccb_hvfs envccnbhv envsshi_onvcana envsshib_hvfs envsshib_onvcana envsshihv envsshihvfs nbias pwrgoodb_onvcc pwrgoodb_or_envcc_onvcc vbias vcc_io vccana_io vccbulk_io vccn_io vss_io vssh_io ioss3_dphy_tx_hvls_hsf

**drv load
*xload vssh_io diffterm vss_io vss_io vss_io vss_io vccn_io vcc_io vssh_io pad dataout vccldo_io vccn_io vss_io ioss3_dphy_tx_txdrv_base_hsio m=4

cload dataout 0 5f


** supply **
vvcc_io vcc_io 0 vc
vvccn_io vccn_io 0 vcn
vvccldo_io vccldo_io 0 vctx
vvccana_io vccana_io 0 vccana
vvssh_io vssh_io 0 vsh
vvss_io vss_io 0 0
vvccbulk_io vccbulk_io 0 vcn

**stimulus**

vnbias nbias vssh_io 0
vvbias vbias vssh_io 0

vpwrgoodb_onvcc pwrgoodb_onvcc 0 0
vpwrgoodb_or_envcc_onvcc pwrgoodb_or_envcc_onvcc 0 0

venvccnbhv envccnbhv 0 vsh

venvcc_onvcc envcc_onvcc 0 0

venvccb_hvfs envccb_hvfs 0 vcn
venbvcc_onvcc enbvcc_onvcc 0 vc
venbvsshi_or_enbvcc_onvcana enbvsshi_or_enbvcc_onvcana 0 vccana

venvsshib_hvfs envsshib_hvfs 0 vcn
venvsshib_onvcana envsshib_onvcana 0 vccana

venvsshihv envsshihv 0 vsh
venvsshihvfs envsshihvfs 0 0
venvsshi_onvcana envsshi_onvcana 0 0

vdata data 0 PULSE ( 0 'vc' 'tdly' 'trf' 'trf' '(prd-2*trf)*0.5' 'prd' )


.tran 20p "15*prd"
.probe
+ v(*) level = 3 filter="*@*" filter="*:*"
+ isub(*)

* 
* 
.mea tran vmax max v(dataout) from="10*prd" to="15*prd"
.mea tran vmin min v(dataout) from="10*prd" to="15*prd"

.mea tran vod_ac param "vmax-vmin"

.mea tran del_rr trig v(data) val="0.5*vc" rise=10 targ v(dataout) val="(vmax+vmin)/2" rise=10
.mea tran del_ff trig v(data) val="0.5*vc" fall=10 targ v(dataout) val="(vmax+vmin)/2" fall=10
 
.mea tran trise trig v(dataout) val="vmin+0.2*vod_ac" rise=10 targ v(dataout) val="vmin+0.8*vod_ac" rise=10
.mea tran tfall trig v(dataout) val="vmin+0.8*vod_ac" fall=10 targ v(dataout) val="vmin+0.2*vod_ac" fall=10

.mea tran tpwd trig v(dataout) val="(vmax+vmin)/2" rise=10 targ v(dataout) val="(vmax+vmin)/2" fall=10 print=0
.mea tran tprd trig v(dataout) val="(vmax+vmin)/2" rise=10 targ v(dataout) val="(vmax+vmin)/2" rise=11 print=0
.mea tran DCD param "tpwd/tprd*100-50"


.end
 

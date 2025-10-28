import sys
import re
import os  

std = sys.argv[1]
Afile=[]
Tfile=[]
CList=[]
Temp=[]
filename=[]
filename1=[]
cal=[]
z=[]
RR=[]
ploc=[]
nloc=[]
start=0
pattern="ABC"
RT=0

if std == "rt":
    RT=1

os.system("ls -d */00bkp_*/report/creport.txt > list.abc")

file2=open("./Clist.abc","w")
file1=open("./list.abc","r")
a=file1.readlines()
for aa in range(len(a)):
    Afile=a[aa].replace("\n","").split("/")
    print(Afile)
    if aa == 0:
        pattern=Afile[0]
        Tfile=Afile
    else:
        match0 = re.search(Afile[0],pattern)
        if match0 is None:
            file2.write(str('/'.join(Tfile))+"\n")
            pattern=Afile[0]
        Tfile=Afile
file2.write(str('/'.join(Afile))+"\n")
file2.close()
os.system("rm ./list.abc")

os.system("mkdir PostProcess")
os.system("mkdir PostProcess/Post")

RR=[]

#ifileA=open("./Clist.abc","r")
#AS=fileA.readlines()
#for ll in range(len(AS)):
#    AS[ll]=AS[ll].replace("\n","")
#    fileB=open("./"+AS[ll],"r")
#    AT=fileB.readlines()
#    for mm in range(len(AT)):
#        matchXZ=re.search("process",AT[mm])
#        if matchXZ is not None:
#            AT[mm]=AT[mm].replace("\t\t","\t")
#            AT[mm]=AT[mm].replace("\t\t","\t")
#            AT[mm]=AT[mm].replace("\t\t","\t")
#            AT[mm]=AT[mm].replace("\t\t","\t")
#            AT[mm]=AT[mm].replace("\t"," ")
#            RR=AT[mm].split(" ")
#            for ix in range(len(RR)): 
#                matchXXZ=re.search("pcode",RR[ix])
#                if matchXXZ is not None:
#                    ploc=ix
#                matchXXZ1=re.search("ncode",RR[ix])
#                if matchXXZ1 is not None:
#                    nloc=ix
#fileA.close()
#fileB.close()

file2=open("./Clist.abc","r")
b=file2.readlines()
for bb in range(len(b)):
    start=0
    lane1=0
    b[bb]=b[bb].replace("\n","")
    filename=b[bb].split("/")
    file3=open("./"+b[bb],"r")
    c=file3.readlines()
    for cc in range(len(c)):
        c[cc]=c[cc].replace("\t\t","\t")
        c[cc]=c[cc].replace("\t\t","\t")
        c[cc]=c[cc].replace("\t\t","\t")
        c[cc]=c[cc].replace("\t\t","\t")
        c[cc]=c[cc].replace("\t"," ")
        matchXZ=re.search("process",c[cc])
        if matchXZ is not None:
            RR=c[cc].split(" ")
            for ix in range(len(RR)):
                matchXXZ=re.search("pcode",RR[ix])
                if matchXXZ is not None:
                    ploc=ix
                matchXXZ1=re.search("ncode",RR[ix])
                if matchXXZ1 is not None:
                    nloc=ix
        Temp=c[cc].split(" ")
        match1 = re.search(Temp[0],"process")
        if match1 is not None:
            start=1
            match2 = re.search("v3",Temp[5])
            if match2 is not None:
                lane1=1
            file4=open("./PostProcess/"+filename[0]+".abc","w")
            file5=open("./PostProcess/Post/"+filename[0]+".abc","w")
        if start == 1:
            matchX = re.search("-40",Temp[2])
            if matchX is not None:
                Temp[2]=Temp[2].replace("-40","m40")
            if lane1==1:
                match3 = re.search("e\+01",Temp[int(ploc)])
                if match3 is not None:
                    cal=Temp[int(ploc)].split("e+")
                    final=float(cal[0])*10
                    match4 = re.search("e\+01",Temp[int(nloc)])
                    if match4 is not None:
                        cal1=Temp[int(nloc)].split("e+")
                        final1=float(cal1[0])*10
                        file4.write(Temp[0]+" "+Temp[2]+" "+Temp[3]+" "+Temp[4]+" "+Temp[5]+" "+Temp[int(ploc)]+" "+Temp[int(nloc)]+"\n")
                        file5.write(Temp[0]+" "+Temp[2]+" "+Temp[3]+" "+Temp[4]+" "+Temp[5]+" "+str(int(final))+" "+str(int(final1))+"\n")
                    else:
                        cal1=Temp[int(nloc)].split(".")
                        file4.write(Temp[0]+" "+Temp[2]+" "+Temp[3]+" "+Temp[4]+" "+Temp[5]+" "+Temp[int(ploc)]+" "+Temp[int(nloc)]+"\n")
                        file5.write(Temp[0]+" "+Temp[2]+" "+Temp[3]+" "+Temp[4]+" "+Temp[5]+" "+str(int(final))+" "+str(cal1[0])+"\n")
                match5 = re.search("e\+00",Temp[int(ploc)])
                if match5 is not None:
                    cal=Temp[int(ploc)].split(".")
                    match6 = re.search("e\+01",Temp[int(nloc)])
                    if match6 is not None:
                        cal1=Temp[int(nloc)].split("e+")
                        final1=float(cal1[0])*10
                        file4.write(Temp[0]+" "+Temp[2]+" "+Temp[3]+" "+Temp[4]+" "+Temp[5]+" "+Temp[int(ploc)]+" "+Temp[int(nloc)]+"\n")
                        file5.write(Temp[0]+" "+Temp[2]+" "+Temp[3]+" "+Temp[4]+" "+Temp[5]+" "+str(int(cal[0]))+" "+str(int(final1))+"\n")
                    else:                
                        cal1=Temp[int(nloc)].split(".")
                        file4.write(Temp[0]+" "+Temp[2]+" "+Temp[3]+" "+Temp[4]+" "+Temp[5]+" "+Temp[int(ploc)]+" "+Temp[int(nloc)]+"\n")
                        file5.write(Temp[0]+" "+Temp[2]+" "+Temp[3]+" "+Temp[4]+" "+Temp[5]+" "+str(int(cal[0]))+" "+str(int(cal1[0]))+"\n")
                    
            else:
                match3 = re.search("e\+01",Temp[int(ploc)])
                if match3 is not None:
                    cal=Temp[int(ploc)].split("e+")
                    final=float(cal[0])*10
                    match4 = re.search("e\+01",Temp[int(nloc)])
                    if match4 is not None:
                        cal1=Temp[int(nloc)].split("e+")
                        final1=float(cal1[0])*10
                        file4.write(Temp[0]+" "+Temp[2]+" "+Temp[3]+" "+Temp[4]+" "+Temp[int(ploc)]+" "+Temp[int(nloc)]+"\n")
                        file5.write(Temp[0]+" "+Temp[2]+" "+Temp[3]+" "+Temp[4]+" "+str(int(final))+" "+str(int(final1))+"\n")
                    else:
                        cal1=Temp[int(nloc)].split(".")
                        file4.write(Temp[0]+" "+Temp[2]+" "+Temp[3]+" "+Temp[4]+" "+Temp[int(ploc)]+" "+Temp[int(nloc)]+"\n")
                        file5.write(Temp[0]+" "+Temp[2]+" "+Temp[3]+" "+Temp[4]+" "+str(int(final))+" "+str(cal1[0])+"\n")
                match5 = re.search("e\+00",Temp[int(ploc)])
                if match5 is not None:
                    cal=Temp[int(ploc)].split(".")
                    match6 = re.search("e\+01",Temp[int(nloc)])
                    if match6 is not None:
                        cal1=Temp[int(nloc)].split("e+")
                        final1=float(cal1[0])*10
                        file4.write(Temp[0]+" "+Temp[2]+" "+Temp[3]+" "+Temp[4]+" "+Temp[int(ploc)]+" "+Temp[int(nloc)]+"\n")
                        file5.write(Temp[0]+" "+Temp[2]+" "+Temp[3]+" "+Temp[4]+" "+str(int(cal[0]))+" "+str(int(final1))+"\n")
                    else:
                        cal1=Temp[int(nloc)].split(".")
                        file4.write(Temp[0]+" "+Temp[2]+" "+Temp[3]+" "+Temp[4]+" "+Temp[int(ploc)]+" "+Temp[int(nloc)]+"\n")
                        file5.write(Temp[0]+" "+Temp[2]+" "+Temp[3]+" "+Temp[4]+" "+str(int(cal[0]))+" "+str(int(cal1[0]))+"\n")
    file4.close()
    file5.close()

os.system("ls ./PostProcess/Post/*.abc > FinalList.abc")
os.system("mkdir ./PostProcess/Post/Lib")

file6=open("./FinalList.abc","r")
e=file6.readlines()
for ee in range(len(e)):
    filename1=e[ee].split("/")
    filename2=filename1[3].split(".")
    fileXX=open("./PostProcess/Post/Lib/"+filename2[0]+".lib","w")
    fileYY=open("./PostProcess/Post/Lib/"+filename2[0]+".csv","w")
    e[ee]=e[ee].replace("\n","")

    corner=["Corner"]
    enable=["Enable"]
    myskew=["myskew"]
    mytemp=["mytemp"]
    vcc=["vcc"]
    vcctx=["vcctx"]
    vccn=["vccn"]
    if RT == 0:
        pu4=["pu4"]
        pu3=["pu3"]
        pu2=["pu2"]
        pu1=["pu1"]
        pu0=["pu0"]
        pd4=["pd4"]
        pd3=["pd3"]
        pd2=["pd2"]
        pd1=["pd1"]
        pd0=["pd0"]
        up4="up_b4"
        up3="up_b3"
        up2="up_b2"
        up1="up_b1"
        up0="up_b0"
        dn4="dn_b4"
        dn3="dn_b3"
        dn2="dn_b2"
        dn1="dn_b1"
        dn0="dn_b0"
    else:
        pu4=["odtpu4"]
        pu3=["odtpu3"]
        pu2=["odtpu2"]
        pu1=["odtpu1"]
        pu0=["odtpu0"]
        pd4=["odtpd4"]
        pd3=["odtpd3"]
        pd2=["odtpd2"]
        pd1=["odtpd1"]
        pd0=["odtpd0"]
        up4="odtpu4"
        up3="odtpu3"
        up2="odtpu2"
        up1="odtpu1"
        up0="odtpu0"
        dn4="odtpd4"
        dn3="odtpd3"
        dn2="odtpd2"
        dn1="odtpd1"
        dn0="odtpd0"

    file7=open("./"+e[ee],"r")
    f=file7.readlines()
    for ff in range(len(f)):
        corner.append("n"+str(int(ff)+1))
        enable.append("t")
        z=f[ff].split(" ")
        myskew.append(z[0])
        mytemp.append(z[1])
        if len(z) == 7:
            z[5]=int(z[5])
            z[6]=int(z[6])
            vcc.append(z[2])
            vcctx.append(z[3])
            vccn.append(z[4])
            #offset
            matchY = re.search("1p1v_pod_rs_",filename2[0])
            if matchY is not None:
                z[6]=z[6]+3
            matchY1 = re.search("_lvstl_rs_",filename2[0])
            if matchY1 is not None:
                 z[5]=z[5]+3
            
            fileXX.write(".lib "+z[0]+"_vcc"+z[2]+"_vcctx"+z[3]+"_vccn"+z[4]+"_"+z[1]+"\n")
            if int(z[5]) > 15:
                fileXX.write(".param "+up4+" = vcc\n")
                pu4.append("1")
                z[5]=z[5]-16
            else:
                fileXX.write(".param "+up4+" = 0\n")
                pu4.append("0")
            if int(z[5]) > 7:
                fileXX.write(".param "+up3+" = vcc\n")
                pu3.append("1")
                z[5]=z[5]-8
            else:
                fileXX.write(".param "+up3+" = 0\n")
                pu3.append("0")
            if int(z[5]) > 3:
                fileXX.write(".param "+up2+" = vcc\n")
                pu2.append("1")
                z[5]=z[5]-4
            else:
                fileXX.write(".param "+up2+" = 0\n")
                pu2.append("0")
            if int(z[5]) > 1:
                fileXX.write(".param "+up1+" = vcc\n")
                pu1.append("1")
                z[5]=z[5]-2
            else:
                fileXX.write(".param "+up1+" = 0\n")
                pu1.append("0")
            if int(z[5]) > 0:
                fileXX.write(".param "+up0+" = vcc\n\n")
                pu0.append("1")
                z[5]=z[5]-1
            else:
                fileXX.write(".param "+up0+" = 0\n\n")
                pu0.append("0")

            if int(z[6]) > 15:
                fileXX.write(".param "+dn4+" = vcc\n")
                pd4.append("1")
                z[6]=z[6]-16
            else:
                fileXX.write(".param "+dn4+" = 0\n")
                pd4.append("0")
            if int(z[6]) > 7:
                fileXX.write(".param "+dn3+" = vcc\n")
                pd3.append("1")
                z[6]=z[6]-8
            else:
                fileXX.write(".param "+dn3+" = 0\n")
                pd3.append("0")
            if int(z[6]) > 3:
                fileXX.write(".param "+dn2+" = vcc\n")
                pd2.append("1")
                z[6]=z[6]-4
            else:
                fileXX.write(".param "+dn2+" = 0\n")
                pd2.append("0")
            if int(z[6]) > 1:
                fileXX.write(".param "+dn1+" = vcc\n")
                pd1.append("1")
                z[6]=z[6]-2
            else:
                fileXX.write(".param "+dn1+" = 0\n")
                pd1.append("0")
            if int(z[6]) > 0:
                fileXX.write(".param "+dn0+" = vcc\n")
                pd0.append("1")
                z[6]=z[6]-1
            else:
                fileXX.write(".param "+dn0+" = 0\n")
                pd0.append("0")
            fileXX.write(".endl\n\n")
        else:
            z[4]=int(z[4])
            z[5]=int(z[5])
            vcc.append(z[2])
            vccn.append(z[3])
            #offset
            matchY2 = re.search("1p1v_pod_rs_",filename2[0])
            if matchY2 is not None:
                z[5]=z[5]+3
            matchY3 = re.search("_lvstl_rs_",filename2[0])
            if matchY3 is not None:
                z[4]=z[4]+3
            fileXX.write(".lib "+z[0]+"_vcc"+z[2]+"_vccn"+z[3]+"_"+z[1]+"\n")
            if int(z[4]) > 15:
                fileXX.write(".param "+up4+" = vcc\n")
                pu4.append("1")
                z[4]=z[4]-16
            else:
                fileXX.write(".param "+up4+" = 0\n")
                pu4.append("0")
            if int(z[4]) > 7:
                fileXX.write(".param "+up3+" = vcc\n")
                pu3.append("1")
                z[4]=z[4]-8
            else:
                fileXX.write(".param "+up3+" = 0\n")
                pu3.append("0")
            if int(z[4]) > 3:
                fileXX.write(".param "+up2+" = vcc\n")
                pu2.append("1")
                z[4]=z[4]-4
            else:
                fileXX.write(".param "+up2+" = 0\n")
                pu2.append("0")
            if int(z[4]) > 1:
                fileXX.write(".param "+up1+" = vcc\n")
                pu1.append("1")
                z[4]=z[4]-2
            else:
                fileXX.write(".param "+up1+" = 0\n")
                pu1.append("0")
            if int(z[4]) > 0:
                fileXX.write(".param "+up0+" = vcc\n\n")
                pu0.append("1")
                z[4]=z[4]-1
            else:
                fileXX.write(".param "+up0+" = 0\n\n")
                pu0.append("0")

            if int(z[5]) > 15:
                fileXX.write(".param "+dn4+" = vcc\n")
                pd4.append("1")
                z[5]=z[5]-16
            else:
                fileXX.write(".param "+dn4+" = 0\n")
                pd4.append("0")
            if int(z[5]) > 7:
                fileXX.write(".param "+dn3+" = vcc\n")
                pd3.append("1")
                z[5]=z[5]-8
            else:
                fileXX.write(".param "+dn3+" = 0\n")
                pd3.append("0")
            if int(z[5]) > 3:
                fileXX.write(".param "+dn2+" = vcc\n")
                pd2.append("1")
                z[5]=z[5]-4
            else:
                fileXX.write(".param "+dn2+" = 0\n")
                pd2.append("0")
            if int(z[5]) > 1:
                fileXX.write(".param "+dn1+" = vcc\n")
                pd1.append("1")
                z[5]=z[5]-2
            else:
                fileXX.write(".param "+dn1+" = 0\n")
                pd1.append("0")
            if int(z[5]) > 0:
                fileXX.write(".param "+dn0+" = vcc\n")
                pd0.append("1")
                z[5]=z[5]-1
            else:
                fileXX.write(".param "+dn0+" = 0\n")
                pd0.append("0")
            fileXX.write(".endl\n\n")
    fileXX.close()
        
    fileYY.write(",".join(corner)+"\n")
    fileYY.write(",".join(enable)+"\n")
    fileYY.write(",".join(myskew)+"\n")
    fileYY.write(",".join(mytemp)+"\n")
    T1=",".join(vcc)
    T1=T1.replace("min","0.675")
    T1=T1.replace("nom","0.75")
    T1=T1.replace("max","0.81")
    fileYY.write(T1+"\n")
    if len(z) == 7:
        T3=",".join(vcctx)
        matchG3=re.search("lvstl_600_rs_",filename2[0])
        if matchG3 is not None:
            T3=T3.replace("min","0.575")
            T3=T3.replace("nom","0.6")
            T3=T3.replace("max","0.625")
        matchG4=re.search("lvstl_650_rs_",filename2[0])
        if matchG4 is not None:
            T3=T3.replace("min","0.625")
            T3=T3.replace("nom","0.65")
            T3=T3.replace("max","0.675")
        matchG5=re.search("lvstl_700_rs_",filename2[0])
        if matchG5 is not None:
            T3=T3.replace("min","0.675")
            T3=T3.replace("nom","0.7")
            T3=T3.replace("max","0.725")
        fileYY.write(T3+"\n")
    T2=",".join(vccn)
    matchG1=re.search("1p05",filename2[0])
    if matchG1 is not None:
        T2=T2.replace("min","0.945")
        T2=T2.replace("nom","1.05")
        T2=T2.replace("max","1.134")
    matchG2=re.search("1p1",filename2[0])
    if matchG2 is not None:
        T2=T2.replace("min","0.99")
        T2=T2.replace("nom","1.1")
        T2=T2.replace("max","1.188")
    fileYY.write(T2+"\n")
    fileYY.write(",".join(pu4)+"\n")
    fileYY.write(",".join(pu3)+"\n")
    fileYY.write(",".join(pu2)+"\n")
    fileYY.write(",".join(pu1)+"\n")
    fileYY.write(",".join(pu0)+"\n")
    fileYY.write(",".join(pd4)+"\n")
    fileYY.write(",".join(pd3)+"\n")
    fileYY.write(",".join(pd2)+"\n")
    fileYY.write(",".join(pd1)+"\n")
    fileYY.write(",".join(pd0)+"\n")
#    print(str(len(corner)))
#    print(str(len(enable)))
#    print(str(len(myskew)))
#    print(str(len(mytemp)))
#    print(str(len(vcc)))
#    if len(z) ==7:
#        print(str(len(vcctx)))
#    print(str(len(vccn)))
#    print(str(len(pu4)))
#    print(str(len(pu3)))
#    print(str(len(pu2)))
#    print(str(len(pu1)))
#    print(str(len(pu0)))
#    print(str(len(pd4)))
#    print(str(len(pd3)))
#    print(str(len(pd2)))
#    print(str(len(pd1)))
#    print(str(len(pd0)))
#    print("finish")

    fileYY.close()


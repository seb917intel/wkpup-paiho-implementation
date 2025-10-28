#!/usr/bin/perl

$infile = shift (@ARGV);
$si_corner = shift (@ARGV);
$ex_corner = shift (@ARGV);
$temperature = shift (@ARGV);
$vtrend_v1 = shift (@ARGV);
$vtrend_v2 = shift (@ARGV);
$vtrend_v3 = shift (@ARGV);
$supply1 = shift (@ARGV);
$supply2 = shift (@ARGV);
$supply3 = shift (@ARGV);
$vccmin = shift (@ARGV);
$vccnom = shift (@ARGV);
$vccmax = shift (@ARGV);
$vcnmin = shift (@ARGV);
$vcnnom = shift (@ARGV);
$vcnmax = shift (@ARGV);
$vccanamin = shift (@ARGV);
$vccananom = shift (@ARGV);
$vccanamax = shift (@ARGV);
$vctxmin = shift (@ARGV);
$vctxnom = shift (@ARGV);
$vctxmax = shift (@ARGV);
$vcc_vid = shift (@ARGV);
$vccmin_tt_h = shift (@ARGV);
$vccnom_tt_h = shift (@ARGV);
$vccmax_tt_h = shift (@ARGV);
$vccmin_tt_c = shift (@ARGV);
$vccnom_tt_c = shift (@ARGV);
$vccmax_tt_c = shift (@ARGV);
$vccmin_ff_h = shift (@ARGV);
$vccnom_ff_h = shift (@ARGV);
$vccmax_ff_h = shift (@ARGV);
$vccmin_ff_c = shift (@ARGV);
$vccnom_ff_c = shift (@ARGV);
$vccmax_ff_c = shift (@ARGV);
$vccmin_ss_h = shift (@ARGV);
$vccnom_ss_h = shift (@ARGV);
$vccmax_ss_h = shift (@ARGV);
$vccmin_ss_c = shift (@ARGV);
$vccnom_ss_c = shift (@ARGV);
$vccmax_ss_c = shift (@ARGV);

# TT FFG FSG SFG SSG FFG_SSG SSG_FFG FFAG SSAG

if ($si_corner eq "TT" || $si_corner eq "FSG" || $si_corner eq "SFG")
{
$vcc_vid_corner = "tt";
}
elsif ($si_corner eq "FFG" || $si_corner eq "FFG_SSG" || $si_corner eq "FFAG")
{
$vcc_vid_corner = "ff";
}
elsif ($si_corner eq "SSG" || $si_corner eq "SSG_FFG" || $si_corner eq "SSAG")
{
$vcc_vid_corner = "ss";
}

else
{
print "error: not valid corner\n";
}

open (INFILE, "< $infile") || die "ERROR: Cannot open input file - $infile\n";

if ($temperature eq "m40")
{
	$temp_num = -40;
}

else
{
	$temp_num = $temperature;
}

$current_directory=`pwd | tr -d '\n'`;


foreach $line (<INFILE>)
{
   chomp ($line);

# update temperature
   if ($line =~ m/.temp /)
   {
	print ".temp $temp_num\n";
   }
# update model file
    elsif ($line =~ m/(.+)DP_HSPICE_MODEL(.+)/)
   {
	print "$1\DP_HSPICE_MODEL\" $si_corner\n";
   }

# update extraction
   elsif ($line =~ m/(.+)\_tparam_typical.spf(.+)/)
   {
	print "$1\_tparam_$ex_corner.spf\"\n";
   }
    elsif ($line =~ m/(.+)\_tparam_typical.red.spf(.+)/)
   {
	print "$1\_tparam_$ex_corner.red.spf\"\n";
   }

#update lib
#    elsif ($line =~ m/(.+)\_rs_lib.lib(.+)/)
#     {
#         if ($supply3 eq "vccn")
#         {
#         #3 supply
#         print "$1\_rs_lib.lib\" $si_corner\_$ex_corner\_$temperature\_v1$vtrend_v1\_v2$vtrend_v2\_v3$vtrend_v3\n";
#         }
#         elsif ($supply2 eq "NA")
#         {
#         #1 supply
#         print "$1\_rs_lib.lib\" $si_corner\_$ex_corner\_$temperature\_v1$vtrend_v1\n";
#         }
#         else
#         {
#         #2 suuply
#         print "$1\_rs_lib.lib\" $si_corner\_$ex_corner\_$temperature\_v1$vtrend_v1\_v2$vtrend_v2\n";
#         }
#     }
#     
#    elsif ($line =~ m/(.+)\_rt_lib.lib(.+)/)
#     {
#         if ($supply3 eq "vccn")
#         {
#         #3 supply
#         print "$1\_rt_lib.lib\" $si_corner\_$ex_corner\_$temperature\_v1$vtrend_v1\_v2$vtrend_v2\_v3$vtrend_v3\n";
#         }
#         elsif ($supply2 eq "NA")
#         {
#         #1 supply
#         print "$1\_rt_lib.lib\" $si_corner\_$ex_corner\_$temperature\_v1$vtrend_v1\n";
#         }
#         else
#         {
#         #2 suuply
#         print "$1\_rt_lib.lib\" $si_corner\_$ex_corner\_$temperature\_v1$vtrend_v1\_v2$vtrend_v2\n";
#         }
#     }
    
   elsif ($line =~ m/(.+)\_lib.lib(.+)/)
    {
        if ($supply3 eq "vccn")
        {
        #3 supply
        print "$1\_lib.lib\" $si_corner\_$ex_corner\_$temperature\_v1$vtrend_v1\_v2$vtrend_v2\_v3$vtrend_v3\n";
        }
        elsif ($supply2 eq "NA")
        {
        #1 supply
        print "$1\_lib.lib\" $si_corner\_$ex_corner\_$temperature\_v1$vtrend_v1\n";
        }
        else
        {
        #2 suuply
        print "$1\_lib.lib\" $si_corner\_$ex_corner\_$temperature\_v1$vtrend_v1\_v2$vtrend_v2\n";
        }
    }

    
# update VCCN
   elsif ($line =~ m/.param vcn=(.+)/)
   {
        if ($supply1 eq "vccn")
        {
            if ($vtrend_v1 eq "max")
            {
                print ".param vcn=$vcnmax\n";
            }
            elsif ($vtrend_v1 eq "nom")
            {
                print ".param vcn=$vcnnom\n";
            }
            elsif ($vtrend_v1 eq "min")
            {
                print ".param vcn=$vcnmin\n";
            }
        }
        elsif ($supply2 eq "vccn")
        {
            if ($vtrend_v2 eq "max")
            {
                print ".param vcn=$vcnmax\n";
            }
            elsif ($vtrend_v2 eq "nom")
            {
                print ".param vcn=$vcnnom\n";
            }
            elsif ($vtrend_v2 eq "min")
            {
                print ".param vcn=$vcnmin\n";
            }
        }
        elsif ($supply3 eq "vccn")
        {
            if ($vtrend_v3 eq "max")
            {
                print ".param vcn=$vcnmax\n";
            }
            elsif ($vtrend_v3 eq "nom")
            {
                print ".param vcn=$vcnnom\n";
            }
            elsif ($vtrend_v3 eq "min")
            {
                print ".param vcn=$vcnmin\n";
            }
        
        }
        else
        {
        print "$line\n";	
        }
    }
    
# update Vssh base on VCCN
#(vcn_nom-0.8)*vcn/vcn_nom+0.05
#(vcn_nom-0.85)*vcn/vcn_nom
#(vcn_nom-0.85)*vcn/vcn_nom-0.05

   elsif ($line =~ m/.param vsh=(.+)/)
   {
        if ($supply1 eq "vccn")
        {
            if ($vtrend_v1 eq "max")
            {
                print ".param vsh=\"(($vcnnom-0.8)*vcn/$vcnnom)+0.05\"\n"; 
            }
            elsif ($vtrend_v1 eq "nom")
            {
                print ".param vsh=\"(($vcnnom-0.85)*vcn/$vcnnom)\"\n"; 
            }
            elsif ($vtrend_v1 eq "min")
            {
                print ".param vsh=\"(($vcnnom-0.85)*vcn/$vcnnom)-0.05\"\n"; 
            }
        }
        elsif ($supply2 eq "vccn")
        {
            if ($vtrend_v2 eq "max")
            {
                print ".param vsh=\"(($vcnnom-0.8)*vcn/$vcnnom)+0.05\"\n"; 
            }
            elsif ($vtrend_v2 eq "nom")
            {
                print ".param vsh=\"(($vcnnom-0.85)*vcn/$vcnnom)\"\n";
            }
            elsif ($vtrend_v2 eq "min")
            {
                print ".param vsh=\"(($vcnnom-0.85)*vcn/$vcnnom)-0.05\"\n"; 
            }
        }
        elsif ($supply3 eq "vccn")
        {
            if ($vtrend_v3 eq "max")
            {
                print ".param vsh=\"(($vcnnom-0.8)*vcn/$vcnnom)+0.05\"\n"; 
            }
            elsif ($vtrend_v3 eq "nom")
            {
                print ".param vsh=\"(($vcnnom-0.85)*vcn/$vcnnom)\"\n";
            }
            elsif ($vtrend_v3 eq "min")
            {
                print ".param vsh=\"(($vcnnom-0.85)*vcn/$vcnnom)-0.05\"\n"; 
            }
        
        }
        else
        {
        print "$line\n";	
        }
    }

    
# update VCC
   elsif ($line =~ m/.param vc=(.+)/)
   {
        if ($supply1 eq "vcc")
        {
            if ($vtrend_v1 eq "max")
            {
                if ($vcc_vid eq "Yes")
                {
                    if ($vcc_vid_corner eq "tt")
                    {
                        if ($temperature eq "m40")
                        {
                            print ".param vc=$vccmax_tt_c\n"; 
                        }
                        elsif ($temperature eq "125")
                        {
                            print ".param vc=$vccmax_tt_h\n"; 
                        }
                        else
                        {
                            print ".param vc=$vccmax\n"; 
                        }
                    }
                    elsif ($vcc_vid_corner eq "ff")
                    {
                        if ($temperature eq "m40")
                        {
                            print ".param vc=$vccmax_ff_c\n"; 
                        }
                        elsif ($temperature eq "125")
                        {
                            print ".param vc=$vccmax_ff_h\n"; 
                        }
                        else
                        {
                            print ".param vc=$vccmax\n"; 
                        }
                    }
                    else
                    {
                        if ($temperature eq "m40")
                        {
                            print ".param vc=$vccmax_ss_c\n"; 
                        }
                        elsif ($temperature eq "125")
                        {
                            print ".param vc=$vccmax_ss_h\n"; 
                        }
                        else
                        {
                            print ".param vc=$vccmax\n"; 
                        }
                    }
                }
                else
                {
                print ".param vc=$vccmax\n";
                }
            }
            elsif ($vtrend_v1 eq "nom")
            {
                if ($vcc_vid eq "Yes")
                {
                    if ($vcc_vid_corner eq "tt")
                    {
                        if ($temperature eq "m40")
                        {
                            print ".param vc=$vccnom_tt_c\n"; 
                        }
                        elsif ($temperature eq "125")
                        {
                            print ".param vc=$vccnom_tt_h\n"; 
                        }
                        else
                        {
                            print ".param vc=$vccnom\n"; 
                        }
                    }
                    elsif ($vcc_vid_corner eq "ff")
                    {
                        if ($temperature eq "m40")
                        {
                            print ".param vc=$vccnom_ff_c\n"; 
                        }
                        elsif ($temperature eq "125")
                        {
                            print ".param vc=$vccnom_ff_h\n"; 
                        }
                        else
                        {
                            print ".param vc=$vccnom\n"; 
                        }
                    }
                    else
                    {
                        if ($temperature eq "m40")
                        {
                            print ".param vc=$vccnom_ss_c\n"; 
                        }
                        elsif ($temperature eq "125")
                        {
                            print ".param vc=$vccnom_ss_h\n"; 
                        }
                        else
                        {
                            print ".param vc=$vccnom\n"; 
                        }
                    }
                }
                else
                {
                print ".param vc=$vccnom\n";
                }
            }
            elsif ($vtrend_v1 eq "min")
            {
                if ($vcc_vid eq "Yes")
                {
                    if ($vcc_vid_corner eq "tt")
                    {
                        if ($temperature eq "m40")
                        {
                            print ".param vc=$vccmin_tt_c\n"; 
                        }
                        elsif ($temperature eq "125")
                        {
                            print ".param vc=$vccmin_tt_h\n"; 
                        }
                        else
                        {
                            print ".param vc=$vccmin\n"; 
                        }
                    }
                    elsif ($vcc_vid_corner eq "ff")
                    {
                        if ($temperature eq "m40")
                        {
                            print ".param vc=$vccmin_ff_c\n"; 
                        }
                        elsif ($temperature eq "125")
                        {
                            print ".param vc=$vccmin_ff_h\n"; 
                        }
                        else
                        {
                            print ".param vc=$vccmin\n"; 
                        }
                    }
                    else
                    {
                        if ($temperature eq "m40")
                        {
                            print ".param vc=$vccmin_ss_c\n"; 
                        }
                        elsif ($temperature eq "125")
                        {
                            print ".param vc=$vccmin_ss_h\n"; 
                        }
                        else
                        {
                            print ".param vc=$vccmin\n"; 
                        } 
                    }
                }
                else
                {
                print ".param vc=$vccmin\n";
                }
            }
        }
        else
        {
        print "$line\n";	
        }
   }
   
# update VCCTX
   elsif ($line =~ m/.param vctx=(.+)/)
   {
        if ($supply2 eq "vcctx")
        {
            if ($vtrend_v2 eq "max")
            {
                print ".param vctx=$vctxmax\n";
            }
            elsif ($vtrend_v2 eq "nom")
            {
                print ".param vctx=$vctxnom\n";
            }
            elsif ($vtrend_v2 eq "min")
            {
                print ".param vctx=$vctxmin\n";
            }
        }
        else
        {
        print ".param vctx=$vctxnom\n";
        #print "$line\n";	
        }
    }
    
# update VCCANA
   elsif ($line =~ m/.param vccana=(.+)/)
   {
        if ($supply1 eq "vccana")
        {
            if ($vtrend_v1 eq "max")
            {
                print ".param vccana=$vccanamax\n";
            }
            elsif ($vtrend_v1 eq "nom")
            {
                print ".param vccana=$vccananom\n";
            }
            elsif ($vtrend_v1 eq "min")
            {
                print ".param vccana=$vccanamin\n";
            }
        }
        elsif ($supply2 eq "vccana")
        {
            if ($vtrend_v2 eq "max")
            {
                print ".param vccana=$vccanamax\n";
            }
            elsif ($vtrend_v2 eq "nom")
            {
                print ".param vccana=$vccananom\n";
            }
            elsif ($vtrend_v2 eq "min")
            {
                print ".param vccana=$vccanamin\n";
            }
        }
        else
        {
        print "$line\n";	
        }
   }

	
   else
   {
	print "$line\n";	
   }
}

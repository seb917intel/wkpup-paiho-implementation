# PVT corners loops

gen_pvt_loop_seq ()
{

if [ "$supply3" == "vccn" ]; then
{
vtrendmax="v1max_v2max_v3max"
vtrendnom="v1nom_v2nom_v3nom"
vtrendall="v1min_v2min_v3min v1min_v2max_v3min v1max_v2min_v3min v1max_v2max_v3min v1min_v2min_v3max v1min_v2max_v3max v1max_v2min_v3max v1max_v2max_v3max v1nom_v2nom_v3nom"
}
elif [ "$supply2" == "NA" ]; then
{
vtrendmax="v1max"
vtrendnom="v1nom"
vtrendall="v1min v1max v1nom"
}
else
{
vtrendmax="v1max_v2max"
vtrendnom="v1nom_v2nom"
vtrendall="v1min_v2min v1min_v2max v1max_v2min v1max_v2max v1nom_v2nom"
}
fi


temperature="m40 125"

if [ "$condition" == "hvqk" ]; then
{
vtrend="$vtrendmax"
}
elif [ "$condition" == "htol" ]; then
{
vtrend="$vtrendmax"
}
else
{
vtrend="$vtrendall"
}
fi

if [ "$mode" == "prelay" ]; then
{
si_corner="$typ_ex_cornerlist"
ex_corner="$typ_ex"
for i in $si_corner
do
	for j in $ex_corner
	do
		for k in $temperature
		do
			if [ $( echo $k | grep -w m40 ) ]; then
				tmp=-40
			else
				tmp=$k
			fi
			for l in $vtrend
			do
			(
			if [ "$supply3" == "vccn" ]; then
			{
                lv1=${l%_*}
				lv1=${lv1%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv2=${lv2%_*}
				lv3=${l#*_v3}
			}
			else
			{
				lv1=${l%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv3="NA"
            }
            fi
				core_func
			)
			done
		done
	done
done
}
else
{
si_corner="$typ_ex_cornerlist"
ex_corner="$typ_ex"
for i in $si_corner
do
	for j in $ex_corner
	do
		for k in $temperature
		do
			if [ $( echo $k | grep -w m40 ) ]; then
				tmp=-40
			else
				tmp=$k
			fi
			for l in $vtrend
			do
			(
			if [ "$supply3" == "vccn" ]; then
			{
                lv1=${l%_*}
				lv1=${lv1%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv2=${lv2%_*}
				lv3=${l#*_v3}
			}
			else
			{
				lv1=${l%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv3="NA"
            }
            fi
				core_func
			)
			done
		done
	done
done

si_corner="$cross_ex_cornerlist"
ex_corner="$cross_ex"
for i in $si_corner
do
	for j in $ex_corner
	do
		for k in $temperature
		do
			if [ $( echo $k | grep -w m40 ) ]; then
				tmp=-40
			else
				tmp=$k
			fi
			for l in $vtrend
			do
			(
			if [ "$supply3" == "vccn" ]; then
			{
                lv1=${l%_*}
				lv1=${lv1%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv2=${lv2%_*}
				lv3=${l#*_v3}
			}
			else
			{
				lv1=${l%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv3="NA"
            }
            fi
				core_func
			)
			done
		done
	done
done
}
fi


temperature="85 100"
si_corner="$typ_corner"
vtrend="$vtrendnom"
ex_corner="$typ_ex"

for i in $si_corner
do
	for j in $ex_corner
	do
		for k in $temperature
		do
			if [ $( echo $k | grep -w m40 ) ]; then
				tmp=-40
			else
				tmp=$k
			fi
			for l in $vtrend
			do
			(
			if [ "$supply3" == "vccn" ]; then
			{
                lv1=${l%_*}
				lv1=${lv1%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv2=${lv2%_*}
				lv3=${l#*_v3}
			}
			else
			{
				lv1=${l%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv3="NA"
            }
            fi
				core_func
			)
			done
		done
	done
done


}

gen_pvt_loop_par ()
{

if [ "$supply3" == "vccn" ]; then
{
vtrendmax="v1max_v2max_v3max"
vtrendnom="v1nom_v2nom_v3nom"
vtrendall="v1min_v2min_v3min v1min_v2max_v3min v1max_v2min_v3min v1max_v2max_v3min v1min_v2min_v3max v1min_v2max_v3max v1max_v2min_v3max v1max_v2max_v3max v1nom_v2nom_v3nom"
}
elif [ "$supply2" == "NA" ]; then
{
vtrendmax="v1max"
vtrendnom="v1nom"
vtrendall="v1min v1max v1nom"
}
else
{
vtrendmax="v1max_v2max"
vtrendnom="v1nom_v2nom"
vtrendall="v1min_v2min v1min_v2max v1max_v2min v1max_v2max v1nom_v2nom"
}
fi

temperature="m40 125"

if [ "$condition" == "hvqk" ]; then
{
vtrend="$vtrendmax"
}
elif [ "$condition" == "htol" ]; then
{
vtrend="$vtrendmax"
}
else
{
vtrend="$vtrendall"
}
fi

if [ "$mode" == "prelay" ]; then
{
si_corner="$typ_ex_cornerlist"
ex_corner="$typ_ex"
for i in $si_corner
do
	for j in $ex_corner
	do
		for k in $temperature
		do
			if [ $( echo $k | grep -w m40 ) ]; then
				tmp=-40
			else
				tmp=$k
			fi
			for l in $vtrend
			do
			(
			if [ "$supply3" == "vccn" ]; then
			{
                lv1=${l%_*}
				lv1=${lv1%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv2=${lv2%_*}
				lv3=${l#*_v3}
			}
			else
			{
				lv1=${l%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv3="NA"
            }
            fi
				core_func
			)&
			done
		done
	done
done
}
else
{
si_corner="$typ_ex_cornerlist"
ex_corner="$typ_ex"

for i in $si_corner
do
	for j in $ex_corner
	do
		for k in $temperature
		do
			if [ $( echo $k | grep -w m40 ) ]; then
				tmp=-40
			else
				tmp=$k
			fi
			for l in $vtrend
			do
			(
			if [ "$supply3" == "vccn" ]; then
			{
                lv1=${l%_*}
				lv1=${lv1%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv2=${lv2%_*}
				lv3=${l#*_v3}
			}
			else
			{
				lv1=${l%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv3="NA"
            }
            fi
				core_func
			)&
			done
		done
	done
done

si_corner="$cross_ex_cornerlist"
ex_corner="$cross_ex"

for i in $si_corner
do
	for j in $ex_corner
	do
		for k in $temperature
		do
			if [ $( echo $k | grep -w m40 ) ]; then
				tmp=-40
			else
				tmp=$k
			fi
			for l in $vtrend
			do
			(
			if [ "$supply3" == "vccn" ]; then
			{
                lv1=${l%_*}
				lv1=${lv1%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv2=${lv2%_*}
				lv3=${l#*_v3}
			}
			else
			{
				lv1=${l%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv3="NA"
            }
            fi
				core_func
			)&
			done
		done
	done
done
}
fi

temperature="85 100"
si_corner="$typ_corner"
vtrend="$vtrendnom"
ex_corner="$typ_ex"

for i in $si_corner
do
	for j in $ex_corner
	do
		for k in $temperature
		do
			if [ $( echo $k | grep -w m40 ) ]; then
				tmp=-40
			else
				tmp=$k
			fi
			for l in $vtrend
			do
			(
			if [ "$supply3" == "vccn" ]; then
			{
                lv1=${l%_*}
				lv1=${lv1%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv2=${lv2%_*}
				lv3=${l#*_v3}
			}
			else
			{
				lv1=${l%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv3="NA"
            }
            fi
				core_func
			)&
			done
		done
	done
done

}

run_pvt_loop_polo ()
{

if [ "$supply3" == "vccn" ]; then
{
vtrendmax="v1max_v2max_v3max"
vtrendnom="v1nom_v2nom_v3nom"
vtrendall="v1min_v2min_v3min v1min_v2max_v3min v1max_v2min_v3min v1max_v2max_v3min v1min_v2min_v3max v1min_v2max_v3max v1max_v2min_v3max v1max_v2max_v3max v1nom_v2nom_v3nom"
}
elif [ "$supply2" == "NA" ]; then
{
vtrendmax="v1max"
vtrendnom="v1nom"
vtrendall="v1min v1max v1nom"
}
else
{
vtrendmax="v1max_v2max"
vtrendnom="v1nom_v2nom"
vtrendall="v1min_v2min v1min_v2max v1max_v2min v1max_v2max v1nom_v2nom"
}
fi


temperature="m40 125"

if [ "$condition" == "hvqk" ]; then
{
vtrend="$vtrendmax"
}
elif [ "$condition" == "htol" ]; then
{
vtrend="$vtrendmax"
}
else
{
vtrend="$vtrendall"
}
fi

if [ "$run_ex_corner" == "tttt" ]; then
{
si_corner="$typ_ex_cornerlist"
ex_corner="$typ_ex"
for i in $si_corner
do
	for j in $ex_corner
	do
		for k in $temperature
		do
			if [ $( echo $k | grep -w m40 ) ]; then
				tmp=-40
			else
				tmp=$k
			fi
			for l in $vtrend
			do
			(
			if [ "$supply3" == "vccn" ]; then
			{
                lv1=${l%_*}
				lv1=${lv1%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv2=${lv2%_*}
				lv3=${l#*_v3}
			}
			else
			{
				lv1=${l%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv3="NA"
            }
            fi
				core_func
			)
			done
		done
	done
done

temperature="85 100"
si_corner="$typ_corner"
vtrend="$vtrendnom"
ex_corner="$typ_ex"

for i in $si_corner
do
	for j in $ex_corner
	do
		for k in $temperature
		do
			if [ $( echo $k | grep -w m40 ) ]; then
				tmp=-40
			else
				tmp=$k
			fi
			for l in $vtrend
			do
			(
			if [ "$supply3" == "vccn" ]; then
			{
                lv1=${l%_*}
				lv1=${lv1%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv2=${lv2%_*}
				lv3=${l#*_v3}
			}
			else
			{
				lv1=${l%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv3="NA"
            }
            fi
				core_func
			)
			done
		done
	done
done

}
else
{
si_corner="$cross_ex_cornerlist"
ex_corner="$run_ex_corner"
for i in $si_corner
do
	for j in $ex_corner
	do
		for k in $temperature
		do
			if [ $( echo $k | grep -w m40 ) ]; then
				tmp=-40
			else
				tmp=$k
			fi
			for l in $vtrend
			do
			(
			if [ "$supply3" == "vccn" ]; then
			{
                lv1=${l%_*}
				lv1=${lv1%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv2=${lv2%_*}
				lv3=${l#*_v3}
			}
			else
			{
				lv1=${l%_*}
				lv1=${lv1#v1}
				lv2=${l#*_v2}
				lv3="NA"
            }
            fi
				core_func
			)
			done
		done
	done
done
}
fi

}



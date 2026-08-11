#!/bin/sh

input_img=$1
echo $1
ref_img=$2
echo $2
diff_img=$3
echo $3
transient_loc=$4
echo $4
output_img_name=$5 
echo $5
validsrc_file=$6
echo $6

#cd gw268092_output

#ds9 $3 -scale limits -10 10 $1 -log -scale limits 1.5 400 -invert -zoom to 2 -pan to $4 wcs fk5 $2 -log -scale limits 1.5 400 -invert -grid grid color black -grid numlab color red -grid axes color red -grid tick color red -grid skyformat degrees -grid yes -frame prev -match frame wcs -region load all validSrc.reg -tile mode column -saveimage jpeg $5 -exit
#ds9 $3 -scale limits -10 10 $1 -log -scale limits 1.5 400 -invert wcs fk5 $2 -log -scale limits 1.5 400 -invert -grid grid color black -grid numlab color red -grid axes color red -grid tick color red -grid skyformat degrees -grid yes -frame prev -match frame wcs -region load all $6 -tile mode column -saveimage jpeg $5 -exit
ds9 $3 -log -scale limits 1.5 400 wcs fk5 $1 -log -scale limits 1.5 400 -invert -zoom to 2 -pan to $4 wcs fk5 $2 -log -scale limits 1.5 400 -invert -grid grid color black -grid numlab color red -grid axes color red -grid tick color red -grid skyformat degrees -grid yes -frame prev -match frame wcs -region load all $6 -tile mode column -saveimage jpeg $5 -exit



#mv $5 Type1a_SN_Output/output_images/
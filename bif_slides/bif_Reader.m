% Roche BIF

%% Example 1
clc;close all;clear
filename1 = '\VT0000194749_D113558_BC286_PDL1.bif';
imf1 = imfinfo(filename1);
disp(imf1(3).ImageDescription)
im1 = imread(imf1(3).Filename,3);
[m,n,c] = size(im1);
imshow(im1)
%zoom-in
imshow(im1(m/3:m/3+512,n/2:n/2+969,:))
imwrite(im1(m/3:m/3+512,n/2:n/2+969,:),'im1.tif')
imwrite(im1(m/3:m/3+512,n/2:n/2+969,:),'im1.png')
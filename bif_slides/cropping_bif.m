%% Crop into patches

%% cleaning
close all;clc;clear
warning('off')

%% data config
abs_path = cd;
path='\Data\';
path_org_out='\Full_slides\';
path_out='\Cropped_slides\';

% enable debug visualization
Debug = 'FALSE';
fgn = 1;

% image quality
L = 3;

% Gray THD
GW_TH = 235;
Mask_TH = 0.7;

% cropped image size
ImgH = 512;
ImgW = 1024;

% reader
imds = dir(path);
img_dirs = {imds.name};
filename_split = split({img_dirs{1,3:end}},".");
filenames = filename_split(1,1:end,1);
num_files = length(filenames);
disp(sprintf('num files are: %d',num_files));

% mkdir output dir
if ~exist(path_out, 'dir')
    mkdir(path_out)
end
if ~exist(path_org_out, 'dir')
    mkdir(path_org_out)
end

%% create folders
for i=1:num_files
    cd(path_org_out)
    mkdir(int2str(i))
    cd(path_out)
    mkdir(int2str(i))
end
cd(abs_path)

%% cropping technique
disp('start cropping')
for i = 1:num_files
    close all
    tic()

    % handle bad format images
    try
        im_file = imfinfo(char(strcat(path,filenames{1,i},".bif")));    
    catch
        continue
    end
    
    if strcmp(Debug,'TRUE')
        disp(im_file(L).ImageDescription)
    end
    
    im = imread(im_file(L).Filename,L);
    [m,n,c] = size(im);
    
    try
        imwrite(im,sprintf('%s/%s/%s.png',path_org_out,string(i),filenames{1,i}));
    catch
        disp('image is very huge, dont save it as one image')
        im_p1 = im(1:m/2,1:n/2,:);
        im_p2 = im((m/2+1):end,(n/2+1):end,:);
        try
            imwrite(im_p1,sprintf('%s/%s/%s_%s.png',path_org_out,string(i),filenames{1,i},"_part_1"));
            imwrite(im_p2,sprintf('%s/%s/%s_%s.png',path_org_out,string(i),filenames{1,i},"_part_2"));
        catch
            disp('image is very huge, dont save it as two images')
            im_p1 = im(1:m/4,1:n/4,:);
            im_p2 = im((m/4+1):(2*m/4),(n/4+1):(2*n/4),:);
            im_p3 = im((2*m/4+1):(3*m/4),(2*n/4+1):(3*n/4),:);
            im_p4 = im((3*m/4+1):end,(3*n/4+1):end,:);
            imwrite(im_p1,sprintf('%s/%s/%s_%s.png',path_org_out,string(i),filenames{1,i},"_part_1"));
            imwrite(im_p2,sprintf('%s/%s/%s_%s.png',path_org_out,string(i),filenames{1,i},"_part_2"));
            imwrite(im_p3,sprintf('%s/%s/%s_%s.png',path_org_out,string(i),filenames{1,i},"_part_3"));
            imwrite(im_p4,sprintf('%s/%s/%s_%s.png',path_org_out,string(i),filenames{1,i},"_part_4"));
        end
    end
    
    if strcmp(Debug,'TRUE')
        figure(fgn);
        imshow(im,[]), title('Original image');
        fgn = fgn + 1;
    end
    
    n_r = floor(m/ImgH);
    n_c = floor(n/ImgW);
    
    cnt = 1;
    for k = 1:n_r
        for j = 1:n_c
            % read patch i,j
            In = im(((k-1)*ImgH+1):(k*ImgH),((j-1)*ImgW+1):(j*ImgW),:);
            Ig = rgb2gray(In);
            Igl = (Ig > GW_TH);
            
            if strcmp(Debug,'TRUE')
                figure(fgn);
                imshow(In,[]), title('Original patch');
                fgn = fgn + 1;
            end
            
            if sum(Igl(:))/(ImgW*ImgH) < Mask_TH
                imwrite(In,sprintf('%s/%s/%s_%d.png',path_out,string(i),filenames{1,i},cnt));
                cnt = cnt + 1;
            end
        end
    end
    disp(sprintf('end cropping image: %d, with %d patches',i, cnt-1));
    toc()
end










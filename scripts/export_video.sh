#!/usr/bin/env bash
set -euo pipefail
cd /mnt/data/factorypulse-d3-final
IN=$(cat assets/video_path.txt)
FONT='FontName=DejaVu Sans,FontSize=19,Bold=1,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=1,Outline=1,Shadow=0,MarginV=34,Alignment=2'
ffmpeg -y -hide_banner -loglevel error -loop 1 -framerate 24 -t 13 -i assets/video_intro.png -vf 'scale=1280:720,format=yuv420p' -c:v libx264 -preset veryfast -crf 22 -pix_fmt yuv420p -an assets/intro.mp4
echo 'Intro encoded'
ffmpeg -y -hide_banner -loglevel error -i "$IN" -vf "fps=24,scale=1280:720,drawbox=x=0:y=610:w=1280:h=110:color=black@0.67:t=fill,subtitles=assets/browser_subtitles.srt:force_style='${FONT}',format=yuv420p" -c:v libx264 -preset veryfast -crf 23 -pix_fmt yuv420p -an assets/browser_captioned.mp4
echo 'Browser encoded'
ffmpeg -y -hide_banner -loglevel error -loop 1 -framerate 24 -t 16 -i assets/video_outro.png -vf 'scale=1280:720,format=yuv420p' -c:v libx264 -preset veryfast -crf 22 -pix_fmt yuv420p -an assets/outro.mp4
echo 'Outro encoded'
printf "file 'assets/intro.mp4'\nfile 'assets/browser_captioned.mp4'\nfile 'assets/outro.mp4'\n" > assets/video_concat.txt
ffmpeg -y -hide_banner -loglevel error -f concat -safe 0 -i assets/video_concat.txt -c copy -movflags +faststart /mnt/data/FactoryPulse_D3_2026_RealBrowser_Demo.mp4
echo 'FINAL VIDEO READY'
ffprobe -v error -show_entries format=duration,size -of json /mnt/data/FactoryPulse_D3_2026_RealBrowser_Demo.mp4

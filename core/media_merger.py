"""
Media Merger Module
Supports merging videos (MP4, AVI, MOV) and PDFs
"""

import os
import tempfile
import subprocess
import sys
from PyPDF2 import PdfMerger
import cv2
import math
from pathlib import Path

class MediaMerger:
    """Class to handle media file merging operations"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.supported_formats = {
            'video': ['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'],
            'pdf': ['pdf']
        }
    
    def is_video_file(self, filename):
        """Check if file is a supported video format"""
        return filename.lower().split('.')[-1] in self.supported_formats['video']
    
    def is_pdf_file(self, filename):
        """Check if file is a supported PDF format"""
        return filename.lower().split('.')[-1] in self.supported_formats['pdf']
    
    def get_file_type(self, filename):
        """Get file type (video or pdf) based on extension"""
        if self.is_video_file(filename):
            return 'video'
        elif self.is_pdf_file(filename):
            return 'pdf'
        else:
            return 'unknown'
    
    # PDF Merging Methods
    def merge_pdfs(self, pdf_paths, output_path):
        """Merge multiple PDF files into one"""
        try:
            merger = PdfMerger()
            
            for pdf_path in pdf_paths:
                if self.is_pdf_file(pdf_path):
                    merger.append(pdf_path)
            
            merger.write(output_path)
            merger.close()
            
            return True
        except Exception as e:
            print(f"PDF merge error: {e}")
            return False
    
    def get_pdf_info(self, pdf_path):
        """Get PDF file information"""
        try:
            merger = PdfMerger()
            merger.append(pdf_path)
            page_count = len(merger.pages)
            merger.close()
            
            file_size = os.path.getsize(pdf_path)
            
            return {
                'type': 'pdf',
                'page_count': page_count,
                'size_mb': round(file_size / (1024 * 1024), 2),
                'file_path': pdf_path
            }
        except Exception as e:
            print(f"PDF info error: {e}")
            return None
    
    # Video Merging Methods
    def merge_videos(self, video_paths, output_path, quality='medium'):
        """Merge multiple video files into one with quality settings"""
        try:
            # Create a temporary file list for FFmpeg
            file_list_path = os.path.join(self.temp_dir, 'file_list.txt')
            
            with open(file_list_path, 'w') as f:
                for video_path in video_paths:
                    f.write(f"file '{video_path}'\n")
            
            # FFmpeg command with quality settings
            quality_settings = {
                'low': ['-crf', '30', '-preset', 'fast'],
                'medium': ['-crf', '23', '-preset', 'medium'],
                'high': ['-crf', '18', '-preset', 'slow']
            }
            
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', file_list_path,
                '-c:v', 'libx264'
            ] + quality_settings.get(quality, quality_settings['medium']) + [
                '-c:a', 'aac',
                '-strict', 'experimental',
                '-y',
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr}")
            return False
        except Exception as e:
            print(f"Video merge error: {e}")
            return False
    
    def get_video_info(self, video_path):
        """Get video file information using OpenCV"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return None
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Get file size
            file_size = os.path.getsize(video_path)
            
            cap.release()
            
            return {
                'type': 'video',
                'duration': duration,
                'duration_str': self.format_duration(duration),
                'size_mb': round(file_size / (1024 * 1024), 2),
                'file_path': video_path
            }
        except Exception as e:
            print(f"Video info error: {e}")
            return None
    
    def format_duration(self, seconds):
        """Format duration in HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    # General Media Processing
    def get_media_info(self, file_paths):
        """Get information about all media files"""
        media_info = []
        
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            
            if self.is_video_file(filename):
                info = self.get_video_info(file_path)
            elif self.is_pdf_file(filename):
                info = self.get_pdf_info(file_path)
            else:
                info = None
            
            if info:
                info['filename'] = filename
                media_info.append(info)
        
        return media_info
    
    def calculate_total_size(self, media_info):
        """Calculate total size of media files in MB"""
        return round(sum(info['size_mb'] for info in media_info), 2)
    
    def calculate_total_duration(self, media_info):
        """Calculate total duration of video files"""
        total_seconds = sum(info['duration'] for info in media_info if info['type'] == 'video')
        return self.format_duration(total_seconds)
    
    def count_files_by_type(self, media_info):
        """Count media files by type"""
        video_count = sum(1 for info in media_info if info['type'] == 'video')
        pdf_count = sum(1 for info in media_info if info['type'] == 'pdf')
        
        return {
            'total': len(media_info),
            'video': video_count,
            'pdf': pdf_count
        }
    
    def validate_media_files(self, file_paths):
        """Validate media files for merging"""
        valid_files = []
        invalid_files = []
        
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            file_type = self.get_file_type(filename)
            
            if file_type == 'unknown':
                invalid_files.append(filename)
                continue
            
            # Check file exists and is readable
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                invalid_files.append(filename)
                continue
            
            # Check file size (max 500MB per file)
            file_size = os.path.getsize(file_path)
            if file_size > 500 * 1024 * 1024:  # 500MB
                invalid_files.append(f"{filename} (file too large)")
                continue
            
            valid_files.append(file_path)
        
        return valid_files, invalid_files
    
    def merge_media(self, file_paths, output_filename, quality='medium'):
        """Merge media files based on type"""
        # Validate files
        valid_files, invalid_files = self.validate_media_files(file_paths)
        
        if not valid_files:
            return None, invalid_files
        
        # Get media information
        media_info = self.get_media_info(valid_files)
        
        # Determine output format
        file_types = set(info['type'] for info in media_info)
        
        if len(file_types) > 1:
            return None, ["Cannot merge different media types (videos and PDFs together)"]
        
        output_dir = tempfile.mkdtemp()
        
        if 'video' in file_types:
            output_path = os.path.join(output_dir, f"{output_filename}.mp4")
            success = self.merge_videos(valid_files, output_path, quality)
        elif 'pdf' in file_types:
            output_path = os.path.join(output_dir, f"{output_filename}.pdf")
            success = self.merge_pdfs(valid_files, output_path)
        else:
            return None, ["Unknown media type"]
        
        if success:
            return output_path, invalid_files
        else:
            return None, ["Merge operation failed"]
    
    def cleanup(self):
        """Clean up temporary directory"""
        import shutil
        
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Cleanup error: {e}")


def main():
    """Test function for media merger"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Media Merger Test')
    parser.add_argument('input_files', nargs='+', help='Input media files to merge')
    parser.add_argument('-o', '--output', required=True, help='Output filename without extension')
    parser.add_argument('-q', '--quality', choices=['low', 'medium', 'high'], 
                        default='medium', help='Output quality (default: medium)')
    
    args = parser.parse_args()
    
    merger = MediaMerger()
    
    try:
        print("Validating files...")
        valid_files, invalid_files = merger.validate_media_files(args.input_files)
        
        if invalid_files:
            print(f"Invalid files: {', '.join(invalid_files)}")
        
        if valid_files:
            print(f"Valid files ({len(valid_files)}):")
            media_info = merger.get_media_info(valid_files)
            
            for info in media_info:
                print(f"  - {info['filename']}")
                if info['type'] == 'video':
                    print(f"    Duration: {info['duration_str']}")
                elif info['type'] == 'pdf':
                    print(f"    Pages: {info['page_count']}")
                print(f"    Size: {info['size_mb']} MB")
            
            # Calculate total info
            count_info = merger.count_files_by_type(media_info)
            total_size = merger.calculate_total_size(media_info)
            
            print(f"\nTotal files: {count_info['total']}")
            if count_info['video'] > 0:
                total_duration = merger.calculate_total_duration(media_info)
                print(f"Total duration: {total_duration}")
            print(f"Total size: {total_size} MB")
            
            print(f"\nMerging with {args.quality} quality...")
            
            output_path, errors = merger.merge_media(
                valid_files, 
                args.output, 
                args.quality
            )
            
            if output_path:
                print(f"Successfully merged to: {output_path}")
            else:
                print(f"Error: {', '.join(errors)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        merger.cleanup()

if __name__ == "__main__":
    main()

"""
Session cleanup utilities
Automatically removes old session files
"""
import os
import time
import shutil
from pathlib import Path
from datetime import datetime, timedelta


class SessionCleaner:
    """Handles automatic cleanup of old session files"""
    
    def __init__(self, upload_folder, output_folder, max_age_hours=24):
        """
        Initialize session cleaner
        
        Args:
            upload_folder: Path to uploads directory
            output_folder: Path to outputs directory
            max_age_hours: Maximum age of sessions in hours before cleanup (can be float for fractions)
        """
        self.upload_folder = Path(upload_folder)
        self.output_folder = Path(output_folder)
        self.max_age_hours = max_age_hours
    
    def cleanup_old_sessions(self):
        """
        Remove session folders older than max_age_hours
        
        Returns:
            dict: Cleanup statistics
        """
        stats = {
            'uploads_cleaned': 0,
            'outputs_cleaned': 0,
            'total_size_freed': 0,
            'errors': []
        }
        
        cutoff_time = time.time() - (self.max_age_hours * 3600)
        
        # Clean upload folders
        stats.update(self._clean_folder(self.upload_folder, cutoff_time, 'uploads_cleaned'))
        
        # Clean output folders
        stats.update(self._clean_folder(self.output_folder, cutoff_time, 'outputs_cleaned'))
        
        return stats
    
    def _clean_folder(self, folder, cutoff_time, stat_key):
        """Clean a specific folder"""
        result = {stat_key: 0, 'total_size_freed': 0, 'errors': []}
        
        if not folder.exists():
            return result
        
        try:
            for session_dir in folder.iterdir():
                if not session_dir.is_dir():
                    continue
                
                # Check folder age
                dir_mtime = session_dir.stat().st_mtime
                
                if dir_mtime < cutoff_time:
                    try:
                        # Calculate folder size
                        folder_size = sum(
                            f.stat().st_size 
                            for f in session_dir.rglob('*') 
                            if f.is_file()
                        )
                        
                        # Remove folder
                        shutil.rmtree(session_dir)
                        
                        result[stat_key] += 1
                        result['total_size_freed'] += folder_size
                        
                    except Exception as e:
                        result['errors'].append(f"Failed to clean {session_dir}: {str(e)}")
        
        except Exception as e:
            result['errors'].append(f"Failed to access {folder}: {str(e)}")
        
        return result
    
    def get_folder_stats(self):
        """
        Get statistics about current sessions
        
        Returns:
            dict: Folder statistics
        """
        stats = {
            'total_sessions': 0,
            'total_size': 0,
            'upload_sessions': 0,
            'upload_size': 0,
            'output_sessions': 0,
            'output_size': 0
        }
        
        # Count uploads
        if self.upload_folder.exists():
            upload_stats = self._get_folder_stats(self.upload_folder)
            stats['upload_sessions'] = upload_stats['count']
            stats['upload_size'] = upload_stats['size']
        
        # Count outputs
        if self.output_folder.exists():
            output_stats = self._get_folder_stats(self.output_folder)
            stats['output_sessions'] = output_stats['count']
            stats['output_size'] = output_stats['size']
        
        stats['total_sessions'] = stats['upload_sessions'] + stats['output_sessions']
        stats['total_size'] = stats['upload_size'] + stats['output_size']
        
        return stats
    
    def _get_folder_stats(self, folder):
        """Get statistics for a specific folder"""
        count = 0
        size = 0
        
        try:
            for session_dir in folder.iterdir():
                if session_dir.is_dir():
                    count += 1
                    size += sum(
                        f.stat().st_size 
                        for f in session_dir.rglob('*') 
                        if f.is_file()
                    )
        except Exception:
            pass
        
        return {'count': count, 'size': size}
    
    def cleanup_specific_session(self, session_id):
        """
        Clean up a specific session by ID
        
        Args:
            session_id: Session ID to clean up
            
        Returns:
            bool: True if successful
        """
        success = True
        
        upload_dir = self.upload_folder / session_id
        output_dir = self.output_folder / session_id
        
        if upload_dir.exists():
            try:
                shutil.rmtree(upload_dir)
            except Exception:
                success = False
        
        if output_dir.exists():
            try:
                shutil.rmtree(output_dir)
            except Exception:
                success = False
        
        return success

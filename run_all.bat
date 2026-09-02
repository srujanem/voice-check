@echo off
echo Starting Master Automation Pipeline...
python grid_search.py
python dataset_scraper.py
python video_processor.py
echo Pipeline Finished!

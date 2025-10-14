""" This module handles graph-related functionalities. Pulling data from Supabase and preparing it for graphing in `graphs.html`. 
"""
from app.supabase_client import supabase
import pandas as pd
import numpy as np
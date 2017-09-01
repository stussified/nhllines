import requests
from flask import Flask, request,session, render_template
import base64
from bs4 import BeautifulSoup
from config import secret_key, CLIENT_ID, SECRET_ID, redirect_url

nhl_schedule_map = {'2017-11-14': ['BUF', 'PIT', 'CBJ', 'MTL', 'DAL', 'FLA', 'WSH', 'NSH', 'PHI', 'MIN', 'ARI', 'WPG', 'VGK', 'EDM', 'VAN', 'LAK'], '2018-04-04': ['OTT', 'BUF', 'CHI', 'STL', 'MIN', 'ANA'], '2017-11-01': ['PHI', 'CHI', 'PIT', 'EDM', 'NJD', 'VAN', 'TOR', 'ANA', 'NSH', 'SJS'], '2017-11-02': ['VGK', 'BOS', 'NYI', 'WSH', 'DET', 'OTT', 'NYR', 'TBL', 'CBJ', 'FLA', 'PHI', 'STL', 'MTL', 'MIN', 'DAL', 'WPG', 'CAR', 'COL', 'PIT', 'CGY', 'BUF', 'ARI', 'TOR', 'LAK'], '2017-11-03': ['NJD', 'EDM', 'NSH', 'ANA'], '2017-11-04': ['VGK', 'OTT', 'TOR', 'STL', 'MTL', 'WPG', 'WSH', 'BOS', 'CBJ', 'TBL', 'NYR', 'FLA', 'COL', 'PHI', 'BUF', 'DAL', 'CHI', 'MIN', 'CAR', 'ARI', 'PIT', 'VAN', 'NSH', 'LAK', 'ANA', 'SJS'], '2017-11-05': ['DET', 'EDM', 'COL', 'NYI', 'MTL', 'CHI', 'NJD', 'CGY'], '2017-11-06': ['MIN', 'BOS', 'VGK', 'TOR', 'CBJ', 'NYR', 'ARI', 'WSH', 'WPG', 'DAL', 'DET', 'VAN'], '2017-11-07': ['WSH', 'BUF', 'STL', 'NJD', 'EDM', 'NYI', 'ARI', 'PIT', 'FLA', 'CAR', 'NSH', 'CBJ', 'VGK', 'MTL', 'VAN', 'CGY', 'LAK', 'ANA'], '2017-11-08': ['MIN', 'TOR', 'BOS', 'NYR', 'TBL', 'SJS'], '2017-11-09': ['EDM', 'NJD', 'CHI', 'PHI', 'MIN', 'MTL', 'ARI', 'STL', 'DET', 'CGY', 'VAN', 'ANA', 'TBL', 'LAK'], '2017-10-14': ['CAR', 'WPG', 'NJD', 'NYR', 'TOR', 'MTL', 'FLA', 'PIT', 'WSH', 'PHI', 'STL', 'TBL', 'COL', 'DAL', 'CBJ', 'MIN', 'NSH', 'CHI', 'BOS', 'ARI', 'CGY', 'VAN', 'OTT', 'EDM', 'NYI', 'SJS', 'BUF', 'LAK'], '2017-10-15': ['BOS', 'VGK', 'BUF', 'ANA', 'NYI', 'LAK'], '2017-10-16': ['TBL', 'DET'], '2017-10-17': ['PIT', 'NYR', 'TOR', 'WSH', 'FLA', 'PHI', 'TBL', 'NJD', 'VAN', 'OTT', 'COL', 'NSH', 'CBJ', 'WPG', 'ARI', 'DAL', 'CAR', 'EDM', 'BUF', 'VGK', 'MTL', 'SJS'], '2017-10-10': ['STL', 'NYR', 'CBJ', 'CAR', 'CHI', 'MTL', 'PHI', 'NSH', 'DET', 'DAL', 'OTT', 'VAN', 'ARI', 'VGK'], '2017-10-11': ['NJD', 'TOR', 'PIT', 'WSH', 'BOS', 'COL', 'NYI', 'ANA', 'CGY', 'LAK'], '2017-10-12': ['PIT', 'TBL', 'STL', 'FLA', 'DAL', 'NSH', 'MIN', 'CHI', 'WPG', 'VAN', 'DET', 'ARI', 'BUF', 'SJS'], '2017-10-13': ['NYR', 'CBJ', 'WSH', 'NJD', 'OTT', 'CGY', 'ANA', 'COL', 'DET', 'VGK'], '2017-12-30': ['BOS', 'OTT', 'MTL', 'FLA', 'NJD', 'WSH', 'CAR', 'STL', 'MIN', 'NSH', 'LAK', 'VAN'], '2017-12-31': ['TOR', 'VGK', 'ARI', 'ANA', 'TBL', 'CBJ', 'WPG', 'EDM', 'PIT', 'DET', 'NYI', 'COL', 'SJS', 'DAL', 'CHI', 'CGY'], '2017-10-18': ['DET', 'TOR', 'CHI', 'STL', 'MTL', 'LAK'], '2017-10-19': ['NYI', 'NYR', 'TBL', 'CBJ', 'NSH', 'PHI', 'VAN', 'BOS', 'NJD', 'OTT', 'EDM', 'CHI', 'CAR', 'CGY', 'STL', 'COL', 'DAL', 'ARI'], '2017-10-05': ['NSH', 'BOS', 'MTL', 'BUF', 'COL', 'NYR', 'WSH', 'OTT', 'MIN', 'DET', 'PIT', 'CHI', 'ARI', 'ANA', 'PHI', 'LAK'], '2017-10-04': ['TOR', 'WPG', 'STL', 'PIT', 'CGY', 'EDM', 'PHI', 'SJS'], '2017-11-17': ['NYR', 'CBJ', 'BUF', 'DET'], '2017-11-16': ['NJD', 'TOR', 'CAR', 'NYI', 'ARI', 'MTL', 'PIT', 'OTT', 'DAL', 'TBL', 'NSH', 'MIN', 'PHI', 'WPG', 'WSH', 'COL', 'STL', 'EDM', 'VGK', 'VAN', 'BOS', 'LAK', 'FLA', 'SJS'], '2017-10-09': ['STL', 'NYI', 'COL', 'BOS', 'NJD', 'BUF', 'CHI', 'TOR', 'WSH', 'TBL', 'WPG', 'EDM', 'CGY', 'ANA'], '2017-10-08': ['MTL', 'NYR'], '2017-11-13': ['DAL', 'CAR', 'STL', 'CGY'], '2017-11-12': ['NJD', 'CHI', 'EDM', 'WSH', 'TBL', 'ANA', 'SJS', 'LAK'], '2017-11-11': ['EDM', 'NYR', 'COL', 'OTT', 'TOR', 'BOS', 'BUF', 'MTL', 'CBJ', 'DET', 'FLA', 'NJD', 'MIN', 'PHI', 'CHI', 'CAR', 'NYI', 'STL', 'PIT', 'NSH', 'VAN', 'SJS', 'WPG', 'ARI'], '2017-11-10': ['OTT', 'COL', 'FLA', 'BUF', 'BOS', 'TOR', 'PIT', 'WSH', 'CAR', 'CBJ', 'NYI', 'DAL', 'WPG', 'VGK'], '2017-10-01': ['WSH', 'STL', 'NYI', 'PHI', 'SJS', 'VGK'], '2017-10-07': ['NYR', 'TOR', 'BUF', 'NYI', 'MTL', 'WSH', 'TBL', 'FLA', 'DET', 'OTT', 'NSH', 'PIT', 'COL', 'NJD', 'MIN', 'CAR', 'DAL', 'STL', 'CBJ', 'CHI', 'VGK', 'ARI', 'PHI', 'ANA', 'EDM', 'VAN', 'WPG', 'CGY', 'LAK', 'SJS'], '2017-10-06': ['NYI', 'CBJ', 'FLA', 'TBL', 'VGK', 'DAL'], '2017-11-19': ['NYI', 'CAR', 'COL', 'DET', 'OTT', 'NYR', 'LAK', 'VGK', 'FLA', 'ANA'], '2017-11-18': ['CGY', 'PHI', 'EDM', 'DAL', 'ARI', 'OTT', 'NJD', 'WPG', 'FLA', 'LAK', 'CAR', 'BUF', 'TOR', 'MTL', 'NYI', 'TBL', 'CHI', 'PIT', 'MIN', 'WSH', 'COL', 'NSH', 'STL', 'VAN', 'BOS', 'SJS'], '2017-12-29': ['BUF', 'NJD', 'CBJ', 'OTT', 'NYR', 'DET', 'PHI', 'TBL', 'PIT', 'CAR', 'NSH', 'MIN', 'NYI', 'WPG', 'STL', 'DAL', 'TOR', 'COL', 'CHI', 'EDM', 'CGY', 'ANA'], '2017-12-28': ['BOS', 'WSH', 'MTL', 'TBL', 'PHI', 'FLA', 'TOR', 'ARI', 'CHI', 'VAN', 'VGK', 'LAK', 'CGY', 'SJS'], '2017-12-27': ['OTT', 'BOS', 'DET', 'NJD', 'BUF', 'NYI', 'CBJ', 'PIT', 'MTL', 'CAR', 'NSH', 'STL', 'DAL', 'MIN', 'EDM', 'WPG', 'WSH', 'NYR', 'ARI', 'COL', 'VGK', 'ANA'], '2017-12-23': ['DET', 'BOS', 'WPG', 'NYI', 'MTL', 'EDM', 'MIN', 'TBL', 'OTT', 'FLA', 'CHI', 'NJD', 'TOR', 'NYR', 'ANA', 'PIT', 'BUF', 'CAR', 'PHI', 'CBJ', 'WSH', 'VGK', 'COL', 'ARI', 'NSH', 'DAL', 'STL', 'VAN', 'LAK', 'SJS'], '2017-12-22': ['PHI', 'BUF', 'MIN', 'FLA', 'MTL', 'CGY', 'WSH', 'ARI'], '2017-12-21': ['WPG', 'BOS', 'NYR', 'NJD', 'ANA', 'NYI', 'CBJ', 'PIT', 'OTT', 'TBL', 'CAR', 'NSH', 'CHI', 'DAL', 'STL', 'EDM', 'COL', 'LAK', 'VAN', 'SJS'], '2017-12-20': ['TOR', 'CBJ', 'DET', 'PHI', 'STL', 'CGY'], '2018-04-01': ['BOS', 'PHI', 'NSH', 'TBL', 'NJD', 'MTL', 'WSH', 'PIT', 'COL', 'ANA'], '2018-01-08': ['CBJ', 'TOR'], '2018-01-09': ['VAN', 'WSH', 'WPG', 'BUF', 'CAR', 'TBL', 'CHI', 'OTT', 'FLA', 'STL', 'CGY', 'MIN', 'EDM', 'NSH'], '2018-03-19': ['NSH', 'BUF', 'CBJ', 'BOS', 'FLA', 'MTL', 'LAK', 'MIN', 'CGY', 'ARI'], '2018-01-02': ['PIT', 'PHI', 'BOS', 'NYI', 'TBL', 'TOR', 'WSH', 'CAR', 'SJS', 'MTL', 'NJD', 'STL', 'FLA', 'MIN', 'CBJ', 'DAL', 'WPG', 'COL', 'LAK', 'EDM', 'NSH', 'VGK', 'ANA', 'VAN'], '2018-01-03': ['OTT', 'DET', 'CHI', 'NYR'], '2018-01-01': ['NYR', 'BUF'], '2018-01-06': ['STL', 'PHI', 'EDM', 'DAL', 'CAR', 'BOS', 'VAN', 'TOR', 'TBL', 'OTT', 'NYR', 'ARI', 'MIN', 'COL', 'ANA', 'CGY', 'NSH', 'LAK'], '2018-01-07': ['NJD', 'NYI', 'BUF', 'PHI', 'EDM', 'CHI', 'SJS', 'WPG', 'STL', 'WSH', 'FLA', 'CBJ', 'VAN', 'MTL', 'TBL', 'DET', 'BOS', 'PIT', 'NYR', 'VGK'], '2018-01-04': ['NYI', 'PHI', 'CAR', 'PIT', 'FLA', 'BOS', 'SJS', 'TOR', 'TBL', 'MTL', 'BUF', 'MIN', 'VGK', 'STL', 'NJD', 'DAL', 'NSH', 'ARI', 'ANA', 'EDM', 'LAK', 'CGY', 'CBJ', 'COL'], '2018-01-05': ['PIT', 'NYI', 'SJS', 'OTT', 'FLA', 'DET', 'BUF', 'WPG', 'VGK', 'CHI'], '2018-04-02': ['BUF', 'TOR', 'WPG', 'OTT', 'CAR', 'FLA', 'WSH', 'STL', 'EDM', 'MIN', 'COL', 'LAK'], '2018-03-28': ['FLA', 'TOR', 'NYR', 'WSH', 'ARI', 'VGK', 'PHI', 'COL'], '2018-03-29': ['PIT', 'NJD', 'TBL', 'BOS', 'DET', 'BUF', 'FLA', 'OTT', 'DAL', 'MIN', 'SJS', 'NSH', 'WPG', 'CHI', 'CBJ', 'CGY', 'EDM', 'VAN', 'ARI', 'LAK'], '2018-03-26': ['BUF', 'TOR', 'OTT', 'CAR', 'FLA', 'NYI', 'WSH', 'NYR', 'DET', 'MTL', 'ARI', 'TBL', 'SJS', 'CHI', 'COL', 'VGK', 'CGY', 'LAK'], '2018-03-27': ['CAR', 'NJD', 'NYI', 'OTT', 'PIT', 'DET', 'BOS', 'WPG', 'SJS', 'STL', 'MIN', 'NSH', 'PHI', 'DAL', 'CBJ', 'EDM', 'ANA', 'VAN'], '2018-03-24': ['VGK', 'COL', 'CGY', 'SJS', 'BUF', 'NYR', 'CAR', 'OTT', 'TBL', 'NJD', 'WSH', 'MTL', 'CHI', 'NYI', 'DET', 'TOR', 'STL', 'CBJ', 'ARI', 'FLA', 'NSH', 'MIN', 'LAK', 'EDM'], '2018-03-25': ['PHI', 'PIT', 'NSH', 'WPG', 'VAN', 'DAL', 'BOS', 'MIN', 'ANA', 'EDM'], '2018-03-22': ['NYR', 'PHI', 'FLA', 'CBJ', 'TBL', 'NYI', 'ARI', 'CAR', 'WSH', 'DET', 'EDM', 'OTT', 'TOR', 'NSH', 'VAN', 'CHI', 'LAK', 'COL', 'VGK', 'SJS'], '2018-03-23': ['NJD', 'PIT', 'MTL', 'BUF', 'VAN', 'STL', 'ANA', 'WPG', 'BOS', 'DAL'], '2018-03-20': ['PIT', 'NYI', 'EDM', 'CAR', 'DAL', 'WSH', 'CBJ', 'NYR', 'PHI', 'DET', 'TOR', 'TBL', 'FLA', 'OTT', 'LAK', 'WPG', 'COL', 'CHI', 'VAN', 'VGK', 'NJD', 'SJS'], '2018-03-21': ['MTL', 'PIT', 'ARI', 'BUF', 'BOS', 'STL', 'ANA', 'CGY'], '2018-03-18': ['DET', 'COL', 'CGY', 'VGK', 'CAR', 'NYI', 'WSH', 'PHI', 'EDM', 'TBL', 'STL', 'CHI', 'DAL', 'WPG', 'NJD', 'ANA'], '2018-04-07': ['NYR', 'PHI', 'CHI', 'WPG', 'OTT', 'BOS', 'MTL', 'TOR', 'NYI', 'DET', 'BUF', 'FLA', 'NJD', 'WSH', 'TBL', 'CAR', 'CBJ', 'NSH', 'ANA', 'ARI', 'STL', 'COL', 'VGK', 'CGY', 'VAN', 'EDM', 'DAL', 'LAK', 'MIN', 'SJS'], '2018-04-06': ['OTT', 'PIT', 'BUF', 'TBL', 'STL', 'CHI', 'DAL', 'ANA'], '2018-04-03': ['NYR', 'NJD', 'PHI', 'NYI', 'DET', 'CBJ', 'WPG', 'MTL', 'BOS', 'TBL', 'NSH', 'FLA', 'ARI', 'CGY', 'VGK', 'VAN', 'DAL', 'SJS'], '2018-01-19': ['MTL', 'WSH', 'VGK', 'FLA', 'LAK', 'ANA'], '2018-01-18': ['BOS', 'NYI', 'TOR', 'PHI', 'WSH', 'NJD', 'DAL', 'CBJ', 'BUF', 'NYR', 'STL', 'OTT', 'VGK', 'TBL', 'ARI', 'NSH', 'SJS', 'COL', 'PIT', 'LAK'], '2018-01-11': ['CAR', 'WSH', 'CBJ', 'BUF', 'CGY', 'TBL'], '2018-01-10': ['OTT', 'TOR', 'MIN', 'CHI'], '2018-01-13': ['NYI', 'NYR', 'DET', 'PIT', 'WPG', 'MIN', 'PHI', 'NJD', 'BOS', 'MTL', 'COL', 'DAL', 'EDM', 'VGK', 'ANA', 'LAK', 'ARI', 'SJS'], '2018-01-12': ['VAN', 'CBJ', 'WSH', 'CAR', 'CGY', 'FLA', 'WPG', 'CHI', 'EDM', 'ARI'], '2018-01-15': ['DAL', 'BOS', 'ANA', 'COL', 'SJS', 'LAK', 'NYI', 'MTL'], '2018-01-14': ['NYR', 'PIT', 'CGY', 'CAR', 'DET', 'CHI', 'VAN', 'MIN'], '2018-01-17': ['MTL', 'BOS', 'PIT', 'ANA'], '2018-01-16': ['NJD', 'NYI', 'PHI', 'NYR', 'STL', 'TOR', 'DAL', 'DET', 'VGK', 'NSH', 'SJS', 'ARI'], '2018-03-31': ['FLA', 'BOS', 'OTT', 'DET', 'CBJ', 'VAN', 'NYI', 'NJD', 'NYR', 'CAR', 'MTL', 'PIT', 'WPG', 'TOR', 'BUF', 'NSH', 'MIN', 'DAL', 'STL', 'ARI', 'EDM', 'CGY', 'SJS', 'VGK'], '2018-03-30': ['TOR', 'NYI', 'CAR', 'WSH', 'TBL', 'NYR', 'CHI', 'COL', 'LAK', 'ANA', 'STL', 'VGK'], '2018-02-21': ['OTT', 'CHI', 'DAL', 'ANA', 'CGY', 'VGK'], '2018-02-20': ['FLA', 'TOR', 'CBJ', 'NJD', 'MTL', 'PHI', 'TBL', 'WSH', 'NSH', 'DET', 'SJS', 'STL', 'LAK', 'WPG', 'BOS', 'EDM', 'COL', 'VAN'], '2018-02-23': ['MIN', 'NYR', 'PIT', 'CAR', 'WPG', 'STL', 'SJS', 'CHI', 'VAN', 'VGK'], '2018-02-22': ['NYI', 'TOR', 'MIN', 'NJD', 'CBJ', 'PHI', 'NYR', 'MTL', 'TBL', 'OTT', 'BUF', 'DET', 'WSH', 'FLA', 'SJS', 'NSH', 'COL', 'EDM', 'CGY', 'ARI', 'DAL', 'LAK'], '2018-02-25': ['BOS', 'BUF', 'STL', 'NSH', 'DET', 'NYR', 'EDM', 'ANA', 'SJS', 'MIN', 'VAN', 'ARI'], '2018-02-24': ['PHI', 'OTT', 'COL', 'CGY', 'WPG', 'DAL', 'BOS', 'TOR', 'TBL', 'MTL', 'CAR', 'DET', 'PIT', 'FLA', 'NYI', 'NJD', 'BUF', 'WSH', 'CHI', 'CBJ', 'ANA', 'ARI', 'EDM', 'LAK'], '2018-02-27': ['CAR', 'BOS', 'NJD', 'PIT', 'OTT', 'WSH', 'TOR', 'FLA', 'STL', 'MIN', 'NSH', 'WPG', 'CGY', 'DAL', 'LAK', 'VGK', 'EDM', 'SJS'], '2018-02-26': ['WSH', 'CBJ', 'PHI', 'MTL', 'TOR', 'TBL', 'VAN', 'COL', 'VGK', 'LAK'], '2018-02-28': ['NYI', 'MTL', 'BUF', 'TBL', 'DET', 'STL', 'CGY', 'COL', 'NYR', 'VAN'], '2018-04-05': ['TOR', 'NJD', 'NYR', 'NYI', 'CAR', 'PHI', 'NSH', 'WSH', 'PIT', 'CBJ', 'MTL', 'DET', 'BOS', 'FLA', 'CGY', 'WPG', 'VGK', 'EDM', 'ARI', 'VAN', 'MIN', 'LAK', 'COL', 'SJS'], '2018-03-16': ['NYI', 'WSH', 'DAL', 'OTT', 'NSH', 'COL', 'SJS', 'CGY', 'DET', 'ANA', 'MIN', 'VGK'], '2018-01-24': ['TOR', 'CHI', 'LAK', 'CGY'], '2018-01-25': ['TBL', 'PHI', 'NSH', 'NJD', 'MIN', 'PIT', 'BOS', 'OTT', 'CAR', 'MTL', 'WSH', 'FLA', 'CHI', 'DET', 'COL', 'STL', 'TOR', 'DAL', 'CGY', 'EDM', 'CBJ', 'ARI', 'NYI', 'VGK', 'BUF', 'VAN', 'WPG', 'ANA', 'NYR', 'SJS'], '2018-01-20': ['NJD', 'PHI', 'DAL', 'BUF', 'NYR', 'COL', 'WPG', 'CGY', 'BOS', 'MTL', 'TOR', 'OTT', 'CAR', 'DET', 'PIT', 'SJS', 'FLA', 'NSH', 'ARI', 'STL', 'NYI', 'CHI', 'TBL', 'MIN', 'VAN', 'EDM'], '2018-01-21': ['PHI', 'WSH', 'VGK', 'CAR', 'VAN', 'WPG', 'SJS', 'ANA', 'NYR', 'LAK'], '2018-01-22': ['DET', 'NJD', 'COL', 'TOR', 'OTT', 'MIN', 'TBL', 'CHI', 'NYI', 'ARI', 'BUF', 'CGY'], '2018-01-23': ['NJD', 'BOS', 'CAR', 'PIT', 'PHI', 'DET', 'COL', 'MTL', 'OTT', 'STL', 'TBL', 'NSH', 'FLA', 'DAL', 'BUF', 'EDM', 'NYR', 'ANA', 'LAK', 'VAN', 'CBJ', 'VGK', 'WPG', 'SJS'], '2018-03-01': ['PIT', 'BOS', 'CAR', 'PHI', 'NJD', 'FLA', 'TBL', 'DAL', 'NSH', 'EDM', 'MIN', 'ARI', 'CHI', 'SJS', 'CBJ', 'LAK'], '2018-03-02': ['MTL', 'NYI', 'NJD', 'CAR', 'BUF', 'FLA', 'DET', 'WPG', 'NYR', 'CGY', 'MIN', 'COL', 'OTT', 'VGK', 'NSH', 'VAN', 'CBJ', 'ANA'], '2018-03-03': ['PHI', 'TBL', 'STL', 'DAL', 'CHI', 'LAK', 'MTL', 'BOS', 'NYI', 'PIT', 'OTT', 'ARI', 'TOR', 'WSH', 'NYR', 'EDM'], '2018-03-04': ['NSH', 'COL', 'PHI', 'FLA', 'CHI', 'ANA', 'VGK', 'NJD', 'DET', 'MIN', 'WPG', 'CAR', 'CBJ', 'SJS'], '2018-03-05': ['CGY', 'PIT', 'TOR', 'BUF', 'OTT', 'DAL', 'ARI', 'EDM', 'NYI', 'VAN'], '2018-03-06': ['MTL', 'NJD', 'DET', 'BOS', 'WPG', 'NYR', 'VGK', 'CBJ', 'FLA', 'TBL', 'CAR', 'MIN', 'DAL', 'NSH', 'COL', 'CHI', 'WSH', 'ANA'], '2018-03-07': ['CGY', 'BUF', 'PIT', 'PHI', 'ARI', 'VAN'], '2018-03-08': ['PHI', 'BOS', 'COL', 'CBJ', 'WPG', 'NJD', 'NYR', 'TBL', 'BUF', 'OTT', 'MTL', 'FLA', 'VGK', 'DET', 'ANA', 'NSH', 'CAR', 'CHI', 'NYI', 'EDM', 'WSH', 'LAK', 'STL', 'SJS'], '2018-03-09': ['DET', 'CBJ', 'CGY', 'OTT', 'ANA', 'DAL', 'MIN', 'VAN'], '2018-03-15': ['TOR', 'BUF', 'WSH', 'NYI', 'CBJ', 'PHI', 'PIT', 'MTL', 'BOS', 'FLA', 'CHI', 'WPG', 'COL', 'STL', 'DET', 'LAK', 'NSH', 'ARI'], '2018-02-14': ['CBJ', 'TOR', 'MTL', 'COL', 'FLA', 'VAN'], '2018-02-15': ['CAR', 'NJD', 'NYR', 'NYI', 'LAK', 'PIT', 'BUF', 'OTT', 'DET', 'TBL', 'CGY', 'NSH', 'WSH', 'MIN', 'ANA', 'CHI', 'MTL', 'ARI', 'EDM', 'VGK', 'VAN', 'SJS'], '2018-02-16': ['PHI', 'CBJ', 'NYI', 'CAR', 'COL', 'WPG', 'STL', 'DAL'], '2018-02-17': ['LAK', 'BUF', 'ANA', 'MIN', 'NYR', 'OTT', 'EDM', 'ARI', 'MTL', 'VGK', 'NJD', 'TBL', 'TOR', 'PIT', 'DET', 'NSH', 'WSH', 'CHI', 'BOS', 'VAN', 'FLA', 'CGY'], '2018-02-10': ['BUF', 'BOS', 'OTT', 'TOR', 'NSH', 'MTL', 'LAK', 'TBL', 'COL', 'CAR', 'NJD', 'CBJ', 'PHI', 'ARI', 'CHI', 'MIN', 'EDM', 'SJS'], '2018-02-11': ['PIT', 'STL', 'NYR', 'WPG', 'DET', 'WSH', 'VAN', 'DAL', 'COL', 'BUF', 'BOS', 'NJD', 'CGY', 'NYI', 'PHI', 'VGK', 'SJS', 'ANA'], '2018-02-12': ['TBL', 'TOR', 'FLA', 'EDM', 'CHI', 'ARI'], '2018-02-13': ['CGY', 'BOS', 'TBL', 'BUF', 'CBJ', 'NYI', 'NJD', 'PHI', 'OTT', 'PIT', 'LAK', 'CAR', 'ANA', 'DET', 'STL', 'NSH', 'NYR', 'MIN', 'WSH', 'WPG', 'CHI', 'VGK', 'ARI', 'SJS'], '2018-02-18': ['PHI', 'NYR', 'EDM', 'COL', 'NJD', 'CAR', 'PIT', 'CBJ', 'TOR', 'DET', 'DAL', 'SJS', 'FLA', 'WPG'], '2018-02-19': ['MIN', 'NYI', 'WSH', 'BUF', 'BOS', 'CGY', 'OTT', 'NSH', 'LAK', 'CHI', 'ANA', 'VGK'], '2018-03-14': ['DAL', 'TOR', 'PIT', 'NYR', 'SJS', 'EDM', 'NJD', 'VGK', 'VAN', 'ANA'], '2018-02-05': ['ANA', 'TOR', 'NSH', 'NYI', 'NYR', 'DAL', 'TBL', 'EDM'], '2018-01-31': ['NYI', 'TOR', 'SJS', 'DET', 'PHI', 'WSH'], '2018-01-30': ['NJD', 'BUF', 'OTT', 'CAR', 'FLA', 'NYI', 'ANA', 'BOS', 'SJS', 'PIT', 'MIN', 'CBJ', 'MTL', 'STL', 'TBL', 'WPG', 'CHI', 'NSH', 'LAK', 'DAL', 'VGK', 'CGY', 'COL', 'VAN'], '2018-03-11': ['BOS', 'CHI', 'NYI', 'CGY', 'DAL', 'PIT', 'VAN', 'ARI'], '2018-03-10': ['MTL', 'TBL', 'CHI', 'BOS', 'WPG', 'PHI', 'VGK', 'BUF', 'ARI', 'COL', 'WSH', 'SJS', 'STL', 'LAK', 'NYR', 'FLA', 'PIT', 'TOR', 'NJD', 'NSH', 'MIN', 'EDM'], '2018-02-02': ['WSH', 'PIT', 'DET', 'CAR', 'SJS', 'CBJ', 'VGK', 'MIN'], '2018-02-03': ['ANA', 'MTL', 'OTT', 'PHI', 'COL', 'WPG', 'TOR', 'BOS', 'STL', 'BUF', 'DET', 'FLA', 'PIT', 'NJD', 'CBJ', 'NYI', 'NYR', 'NSH', 'MIN', 'DAL', 'TBL', 'VAN', 'CHI', 'CGY', 'ARI', 'LAK'], '2018-02-09': ['DET', 'NYI', 'CGY', 'NYR', 'CBJ', 'WSH', 'LAK', 'FLA', 'VAN', 'CAR', 'STL', 'WPG', 'PIT', 'DAL', 'EDM', 'ANA'], '2018-02-08': ['NYI', 'BUF', 'CGY', 'NJD', 'MTL', 'PHI', 'NSH', 'OTT', 'VAN', 'TBL', 'COL', 'STL', 'ARI', 'MIN', 'DAL', 'CHI', 'VGK', 'SJS'], '2018-03-13': ['BOS', 'CAR', 'OTT', 'TBL', 'DAL', 'MTL', 'WPG', 'NSH', 'COL', 'MIN', 'EDM', 'CGY', 'LAK', 'ARI'], '2018-03-12': ['MTL', 'CBJ', 'CAR', 'NYR', 'WPG', 'WSH', 'VGK', 'PHI', 'OTT', 'FLA', 'STL', 'ANA', 'DET', 'SJS', 'VAN', 'LAK'], '2017-11-28': ['TBL', 'BUF', 'VAN', 'NYI', 'FLA', 'NYR', 'SJS', 'PHI', 'CAR', 'CBJ', 'LAK', 'DET', 'CHI', 'NSH', 'TOR', 'CGY', 'ARI', 'EDM', 'DAL', 'VGK'], '2017-11-29': ['TBL', 'BOS', 'OTT', 'MTL', 'ANA', 'STL', 'WPG', 'COL'], '2017-11-26': ['NSH', 'CAR', 'VAN', 'NYR', 'EDM', 'BOS'], '2017-11-27': ['FLA', 'NJD', 'PHI', 'PIT', 'CBJ', 'MTL', 'MIN', 'WPG', 'ANA', 'CHI'], '2017-11-24': ['PIT', 'BOS', 'WPG', 'ANA', 'COL', 'MIN', 'NYI', 'PHI', 'TBL', 'WSH', 'SJS', 'VGK', 'EDM', 'BUF', 'VAN', 'NJD', 'DET', 'NYR', 'OTT', 'CBJ', 'TOR', 'CAR', 'NSH', 'STL', 'LAK', 'ARI', 'CGY', 'DAL'], '2017-11-25': ['WSH', 'TOR', 'BUF', 'MTL', 'NYI', 'OTT', 'NJD', 'DET', 'CHI', 'FLA', 'TBL', 'PIT', 'VGK', 'ARI', 'MIN', 'STL', 'WPG', 'SJS', 'CGY', 'COL', 'ANA', 'LAK'], '2017-11-22': ['MIN', 'BUF', 'EDM', 'DET', 'TOR', 'FLA', 'BOS', 'NJD', 'PHI', 'NYI', 'VAN', 'PIT', 'OTT', 'WSH', 'NYR', 'CAR', 'CGY', 'CBJ', 'CHI', 'TBL', 'MTL', 'NSH', 'DAL', 'COL', 'SJS', 'ARI', 'VGK', 'ANA', 'WPG', 'LAK'], '2018-02-01': ['STL', 'BOS', 'FLA', 'BUF', 'PHI', 'NJD', 'TOR', 'NYR', 'MTL', 'CAR', 'ANA', 'OTT', 'VGK', 'WPG', 'LAK', 'NSH', 'TBL', 'CGY', 'COL', 'EDM', 'DAL', 'ARI', 'CHI', 'VAN'], '2017-11-20': ['CBJ', 'BUF', 'ARI', 'TOR', 'CGY', 'WSH', 'WPG', 'NSH', 'NJD', 'MIN', 'ANA', 'SJS'], '2017-11-21': ['VAN', 'PHI', 'EDM', 'STL', 'MTL', 'DAL'], '2017-10-30': ['BOS', 'CBJ', 'ARI', 'PHI', 'VGK', 'NYI', 'MTL', 'OTT', 'TBL', 'FLA', 'LAK', 'STL', 'DAL', 'VAN', 'TOR', 'SJS'], '2017-10-31': ['VGK', 'NYR', 'ARI', 'DET', 'WPG', 'MIN'], '2018-02-07': ['NSH', 'TOR', 'BOS', 'NYR', 'EDM', 'LAK'], '2018-02-06': ['ANA', 'BUF', 'VGK', 'PIT', 'PHI', 'CAR', 'WSH', 'CBJ', 'NJD', 'OTT', 'BOS', 'DET', 'VAN', 'FLA', 'MIN', 'STL', 'ARI', 'WPG', 'CGY', 'CHI', 'SJS', 'COL'], '2017-12-16': ['EDM', 'MIN', 'NYR', 'BOS', 'WPG', 'STL', 'MTL', 'OTT', 'LAK', 'NYI', 'DAL', 'PHI', 'PIT', 'ARI', 'ANA', 'WSH', 'CBJ', 'CAR', 'TBL', 'COL', 'NSH', 'CGY'], '2017-12-17': ['STL', 'WPG', 'MIN', 'CHI', 'CGY', 'VAN', 'FLA', 'VGK'], '2017-12-14': ['WSH', 'BOS', 'BUF', 'PHI', 'NYI', 'CBJ', 'NJD', 'MTL', 'ANA', 'STL', 'TOR', 'MIN', 'CHI', 'WPG', 'FLA', 'COL', 'SJS', 'CGY', 'NSH', 'EDM', 'TBL', 'ARI', 'PIT', 'VGK'], '2017-12-15': ['CAR', 'BUF', 'DAL', 'NJD', 'LAK', 'NYR', 'TOR', 'DET', 'SJS', 'VAN'], '2017-12-12': ['OTT', 'BUF', 'LAK', 'NJD', 'TOR', 'PHI', 'COL', 'WSH', 'EDM', 'CBJ', 'TBL', 'STL', 'CGY', 'MIN', 'FLA', 'CHI', 'CAR', 'VGK'], '2017-12-13': ['NYR', 'OTT', 'DAL', 'NYI', 'BOS', 'DET', 'NSH', 'VAN'], '2017-12-10': ['ARI', 'CHI', 'BUF', 'STL', 'EDM', 'TOR', 'MIN', 'SJS'], '2017-12-11': ['WSH', 'NYI', 'DAL', 'NYR', 'COL', 'PIT', 'FLA', 'DET', 'VAN', 'WPG', 'CAR', 'ANA'], '2018-02-04': ['VGK', 'WSH', 'OTT', 'MTL', 'SJS', 'CAR'], '2017-12-18': ['CBJ', 'BOS', 'ANA', 'NJD', 'LAK', 'PHI', 'PIT', 'COL', 'SJS', 'EDM'], '2017-12-19': ['CAR', 'TOR', 'DET', 'NYI', 'ANA', 'NYR', 'MIN', 'OTT', 'BOS', 'BUF', 'WPG', 'NSH', 'WSH', 'DAL', 'FLA', 'ARI', 'MTL', 'VAN', 'TBL', 'VGK'], '2018-03-17': ['CHI', 'BUF', 'EDM', 'FLA', 'NJD', 'LAK', 'PHI', 'CAR', 'BOS', 'TBL', 'MTL', 'TOR', 'OTT', 'CBJ', 'NYR', 'STL', 'MIN', 'ARI', 'SJS', 'VAN'], '2017-11-30': ['LAK', 'WSH', 'MTL', 'DET', 'VAN', 'NSH', 'VGK', 'MIN', 'DAL', 'CHI', 'ARI', 'CGY', 'TOR', 'EDM'], '2017-10-21': ['NSH', 'NYR', 'EDM', 'PHI', 'BUF', 'BOS', 'TOR', 'OTT', 'PIT', 'TBL', 'SJS', 'NYI', 'LAK', 'CBJ', 'FLA', 'WSH', 'CAR', 'DAL', 'CHI', 'ARI', 'MIN', 'CGY', 'STL', 'VGK'], '2017-10-20': ['VAN', 'BUF', 'SJS', 'NJD', 'WSH', 'DET', 'PIT', 'FLA', 'MIN', 'WPG', 'MTL', 'ANA'], '2017-10-23': ['LAK', 'TOR', 'SJS', 'NYR'], '2017-10-22': ['VAN', 'DET'], '2017-10-25': ['CGY', 'STL', 'BUF', 'CBJ'], '2017-10-24': ['ARI', 'NYI', 'ANA', 'PHI', 'EDM', 'PIT', 'TBL', 'CAR', 'DET', 'BUF', 'FLA', 'MTL', 'LAK', 'OTT', 'CGY', 'NSH', 'VAN', 'MIN', 'DAL', 'COL', 'CHI', 'VGK'], '2017-10-27': ['COL', 'VGK', 'OTT', 'NJD', 'WPG', 'CBJ', 'STL', 'CAR', 'NSH', 'CHI', 'DAL', 'CGY'], '2017-10-26': ['CAR', 'TOR', 'SJS', 'BOS', 'WPG', 'PIT', 'ARI', 'NYR', 'PHI', 'OTT', 'DET', 'TBL', 'ANA', 'FLA', 'LAK', 'MTL', 'NYI', 'MIN', 'DAL', 'EDM', 'WSH', 'VAN'], '2017-10-29': ['ANA', 'CAR', 'PIT', 'WPG', 'WSH', 'CGY'], '2017-10-28': ['SJS', 'BUF', 'NYR', 'MTL', 'PHI', 'TOR', 'DET', 'FLA', 'ANA', 'TBL', 'LAK', 'BOS', 'ARI', 'NJD', 'NYI', 'NSH', 'PIT', 'MIN', 'CBJ', 'STL', 'CHI', 'COL', 'WSH', 'EDM'], '2017-11-15': ['CGY', 'DET', 'NYR', 'CHI', 'BOS', 'ANA'], '2017-12-05': ['NJD', 'CBJ', 'NYR', 'PIT', 'STL', 'MTL', 'WPG', 'DET', 'NYI', 'TBL', 'NSH', 'DAL', 'BUF', 'COL', 'CAR', 'VAN', 'ANA', 'VGK', 'MIN', 'LAK'], '2017-12-04': ['SJS', 'WSH', 'NYI', 'FLA', 'BOS', 'NSH', 'PHI', 'CGY'], '2017-12-07': ['ARI', 'BOS', 'NYI', 'PIT', 'CGY', 'MTL', 'COL', 'TBL', 'WPG', 'FLA', 'DAL', 'STL', 'PHI', 'VAN', 'OTT', 'LAK', 'CAR', 'SJS'], '2017-12-06': ['CGY', 'TOR', 'CHI', 'WSH', 'PHI', 'EDM', 'OTT', 'ANA'], '2017-12-01': ['PIT', 'BUF', 'OTT', 'NYI', 'CAR', 'NYR', 'ANA', 'CBJ', 'SJS', 'FLA', 'LAK', 'STL', 'VGK', 'WPG', 'NJD', 'COL'], '2017-12-03': ['LAK', 'CHI', 'OTT', 'WPG', 'ARI', 'VGK', 'DAL', 'COL'], '2017-12-02': ['BOS', 'PHI', 'STL', 'MIN', 'TOR', 'VAN', 'DET', 'MTL', 'SJS', 'TBL', 'BUF', 'PIT', 'CBJ', 'WSH', 'NJD', 'ARI', 'ANA', 'NSH', 'FLA', 'CAR', 'CHI', 'DAL', 'EDM', 'CGY'], '2017-12-09': ['STL', 'DET', 'NYI', 'BOS', 'EDM', 'MTL', 'WPG', 'TBL', 'COL', 'FLA', 'NJD', 'NYR', 'TOR', 'PIT', 'ARI', 'CBJ', 'VGK', 'DAL', 'OTT', 'SJS', 'VAN', 'CGY', 'CAR', 'LAK'], '2017-12-08': ['CBJ', 'NJD', 'NYR', 'WSH', 'VGK', 'NSH', 'BUF', 'CHI', 'MIN', 'ANA']}

nhl_to_yahoo_abbr = {
    "MIN":"MIN",
    "NYR":"NYR",
    "WAS":"WSH",
    "BOS":"BOS",
    "DET":"DET",
    "NYI":"NYI",
    "FLA":"FLA",
    "COL":"COL",
    "NSH":"NSH",
    "NJ":"NJD",
    "DAL":"DAL",
    "CGY":"CGY",
    "TOR":"TOR",
    "CAR":"CAR",
    "WPG":"WPG",
    "BUF":"BUF",
    "VAN":"VAN",
    "VGK":"VGK",
    "STL":"STL",
    "CHI":"CHI",
    "SJ":"SJS",
    "MON":"MTL",
    "PHI":"PHI",
    "ANH":"ANA",
    "LA":"LAK",
    "CLS":"CBJ",
    "PIT":"PIT",
    "EDM":"EDM",
    "TB":"TBL",
    "ARI":"ARI",
    "OTT":"OTT"
}


app = Flask(__name__)
app.secret_key = secret_key

def oauth_auth_url():
    url = "https://api.login.yahoo.com/oauth2/request_auth?client_id=%s&redirect_uri=%s&response_type=code" % (
    CLIENT_ID, redirect_url)
    return url

@app.route('/')
def index():
    return render_template("index.html", oauth_auth_url = oauth_auth_url())


@app.route("/redirect", methods=["GET"])
def redirect():
    code = request.args.get("code")
    access_token = get_token(code)

    if not access_token:
        return "Oops -  looks like something broke."

    headers = oauth_headers(access_token)
    session["headers"] = headers
    team_list = select_team(headers)

    if team_list:
        return render_template("select_lines.html", team_list=team_list)
    else:
        return "You don't have an NHL team for the 2017-2018 season."


@app.route('/run', methods=["POST"])
def run_lines():
    print session
    if "headers" in session:
        headers = session['headers']
        print headers
    else:
        return "Oauth didn't work correctly"

    team_id = request.form["team"]

    # get roster
    roster = get_roster(headers, team_id)
    roster_list = build_lineup(roster)
    for roster_xml in roster_list:
        put_roster(headers, team_id, roster_xml)

    return "Your lines should be now set, however some multi-positional players might be benched when you could be active.  I will hopefully fix this later."


def get_token(code):
    token_url = "https://api.login.yahoo.com/oauth2/get_token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": SECRET_ID,
        "redirect_uri": "oob",
        "code": code,
        "grant_type": "authorization_code"
    }

    headers = {
        "Authorization": "Basic %s" % base64.b64encode("%s:%s" % (CLIENT_ID, SECRET_ID)),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    r = requests.post(token_url, headers=headers, data=data)
    access_token = r.json().get("access_token")

    if r.status_code == 200:
        return access_token
    else:
        return False


def oauth_headers(access_token):
    return {"Authorization": "Bearer %s" % access_token}


def select_team(headers):
    url = "https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;game_codes=nhl;seasons=2017/teams"
    r = requests.get(url, headers = headers)

    if r.status_code != 200:
        return "something broke - you might not have a team?"

    team_dict = {}
    soup = BeautifulSoup(r.content, "lxml")
    teams = soup.find_all("team")
    for team in teams:
        team_dict[team.find("name").text] = team.find("team_key").text

    return team_dict

# roster is used multiple times, write function so it can be stored as a variable

def get_roster(headers, team_id):
    url = "https://fantasysports.yahooapis.com/fantasy/v2/team/%s/players;sort=OR" % team_id
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        return "Something broke - invalid team id"

    return r.content


# dictionary with a breakdown of positions i.e. {u'C': 2, u'RW': 2, u'D': 4, u'G': 2, u'BN': 4, u'LW': 2}
# TODO add check for non standard roster positions

def get_roster_breakdown(roster_xml):
    roster = BeautifulSoup(roster_xml, 'lxml')
    lineup = []
    final_count = {}

    for player in roster.find_all("player"):
        # can return a blank player some how? adding check
        if player.find("eligible_positions"):
            lineup.append(player.find("eligible_positions").find("position").text)
    positions = set(lineup)

    for position in positions:
        final_count[position] = lineup.count(position)

    return final_count

# rank the roster in a way that we can use
def get_roster_rank(roster_xml):
    roster = BeautifulSoup(roster_xml, 'lxml')
    ranked_list = []
    rank = 1
    for player in roster.find_all("player"):
        # can return a blank for some reason, just adding a check
        if player.find("full"):
            full_name = player.find("full").text
            position_list = []
            for positions in player.find("eligible_positions"):
                if positions.string != "\n":
                    position_list.append(positions.string)

            player_dict = {
                "name": full_name,
                "player_key": player.find("editorial_player_key").text,
                "team_key": player.find("editorial_team_abbr").text.upper(),
                "positions": position_list,
                "rank": rank,
                "selected": False
            }

            ranked_list.append(player_dict)
            rank += 1
    return ranked_list

# this actually builds the xml to create a roster
def build_lineup(raw_roster):
    roster_list = []
    for date, active_teams in nhl_schedule_map.items():
        players = get_roster_rank(raw_roster)
        # breakdown = get_roster_breakdown(raw_roster) # currently just using the default yahoo roster counts
        breakdown = {"G":2, "RW":2, "LW": 2, "D": 4, "C": 2}
        daily_lineup = []
        used_player = []

        # TODO - logic needs to be improved, some players that can play multiple positions will be left out even if one of their slots are empty
        for pos, count in breakdown.items():
            for player in players:
                if nhl_to_yahoo_abbr.get(player.get("team_key")) in active_teams and player.get("player_key") not in used_player:
                    # run this twice to get multi positioned players
                    if pos in player.get("positions") and int(count) != 0:
                        count = int(count) - 1
                        player['positions'] = pos
                        daily_lineup.append(player)
                        used_player.append(player.get("player_key"))

        for player in players:
            if player.get("player_key") not in used_player:
                player['positions'] = "BN"
                daily_lineup.append(player)

        player_xml_list = []
        for player in daily_lineup:
            player_xml = """
                <player>
                    <player_key>%s</player_key>
                    <position>%s</position>
                </player>
            """ % (player.get("player_key"), player.get("positions"))
            player_xml_list.append(player_xml)
        roster_xml = """
        <?xml version="1.0"?>
            <fantasy_content>
              <roster>
                <coverage_type>date</coverage_type>
                <date>%s</date>

                <players>
                    %s
                </players>
              </roster>
        </fantasy_content>
        """ % (date, "".join(player_xml_list))

        roster_list.append(roster_xml)

    return roster_list

def put_roster(headers, team_id, roster):
    headers['Content-Type'] = 'application/xml'
    url = "https://fantasysports.yahooapis.com/fantasy/v2/team/%s/roster" % team_id
    soup = BeautifulSoup(roster, 'lxml')
    print soup.find("date").text
    r = requests.put(url, headers=headers, data=roster.strip())
    if "That position has already been filled" in r.content:
        print roster.strip()

    if r.status_code != 200:
        return "Something broke - invalid roster xml?"


if __name__ == "__main__":
    app.run(debug=True)

"""database update functions
"""
# -- Imports --------------------------------------------------------------------------
from datetime import datetime

import pandas as pd

from basketball_db.extract import (
    get_box_score_summaries,
    get_draft_combine_stats,
    get_draft_history,
    get_league_game_log_from_date,
    get_play_by_play,
    get_player_game_logs,
    get_player_info,
    get_players,
    get_team_info_common,
    get_teams,
    get_teams_details,
)
from basketball_db.utils import (
    download_db,
    dump_db,
    get_db_conn,
    get_proxies,
    upload_new_db_version,
)


# -- Functions -----------------------------------------------------------------------
def daily():
    # download db from Kaggle
    download_db()
    # get proxies and establish db connenction
    proxies = get_proxies()
    conn = get_db_conn()
    # get latest date in db and add a day
    latest_db_date = pd.read_sql("SELECT MAX(GAME_DATE) FROM game", conn).iloc[0, 0]
    latest_db_date = pd.to_datetime(latest_db_date) + pd.Timedelta(days=1)
    # get new games and add to db
    df = get_league_game_log_from_date(latest_db_date, proxies, save_to_db=True, conn=conn)
    games = df['game_id'].unique().tolist()
    # get box score summaries and play by play for new games
    get_box_score_summaries(games, proxies, save_to_db=True, conn=conn)
    get_play_by_play(games, proxies, save_to_db=True, conn=conn)
    # dump db tables to csv
    dump_db(conn)
    # upload new db version to Kaggle
    version_message = f"Daily update: {pd.to_datetime('today').strftime('%Y-%m-%d')}"
    upload_new_db_version(version_message)
    # close db connection
    conn.close()


def monthly():
    # download db from Kaggle
    download_db()
    # get proxies and establish db connenction
    proxies = get_proxies()
    conn = get_db_conn()
    # update players & teams
    get_players(save_to_db=True, conn=conn)
    get_teams(save_to_db=True, conn=conn)
    get_player_info(proxies=proxies, save_to_db=True, conn=conn)
    get_teams_details(proxies=proxies, save_to_db=True, conn=conn)
    most_recent_draft_season = pd.read_sql("SELECT MAX(SEASON) FROM draft_combine_stats", conn).iloc[0, 0]
    if datetime.today().year > most_recent_draft_season:
        get_draft_combine_stats(proxies=proxies, season=str(datetime.today().year), save_to_db=True, conn=conn)
        get_draft_history(proxies=proxies, season=str(datetime.today().year), save_to_db=True, conn=conn)
    get_team_info_common(proxies=proxies, save_to_db=True, conn=conn)
    get_player_game_logs(proxies=proxies, save_to_db=True, conn=conn)
    # upload new db version to Kaggle
    version_message = f"Monthly update: {pd.to_datetime('today').strftime('%Y-%m-%d')}"
    upload_new_db_version(version_message)
    # close db connection
    conn.close()
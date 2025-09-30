import sys
import os
import pandas as pd
import plotly.express as px


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from backend.db_utils import connect_db, get_all_commits, TABLE


def repo_metrics_distribution(selected_repos=None):
    conn, cur = connect_db()
    
    # Get all repo data
    query = f"""
        SELECT repo_name, total_commits, files_count, languages
        FROM {TABLE}
        {f"WHERE repo_name = ANY(%s)" if selected_repos else ""}
        """
    cur.execute(query, [selected_repos] if selected_repos else None)

    data = cur.fetchall()
    
    # Convert to DataFrame
    df = pd.DataFrame(data, columns=['repo_name', 'total_commits', 'files_count', 'languages'])
    
    # Create visualizations
    fig_commits = px.histogram(df, x='total_commits', nbins=10, 
                             title='Distribution of Total Commits',
                             color_discrete_sequence=['skyblue'])
    
    fig_files = px.histogram(df, x='files_count',
                            title='Number of Files by Repository',
                            color='repo_name')
    
    # Box plot of commits
    fig_box = px.box(df, y='total_commits',
                     title='Commit Distribution Across Repositories',
                     points='all')
    
    # Violin plot
    fig_violin = px.violin(df, y='total_commits',
                          box=True, points='all',
                          title='Violin Plot of Commit Distribution')
    
    # Language distribution heatmap
    language_data = []
    for _, row in df.iterrows():
        if isinstance(row['languages'], dict):
            for lang, count in row['languages'].items():
                language_data.append({
                    'repo': row['repo_name'],
                    'language': lang,
                    'count': count
                })
    
    lang_df = pd.DataFrame(language_data)
    lang_pivot = lang_df.pivot(index='repo', columns='language', values='count').fillna(0)
    
    fig_lang_heatmap = px.imshow(lang_pivot,
                                title='Language Usage Across Repositories',
                                color_continuous_scale='RdBu_r')
    
    # Correlation heatmap
    corr = df[['total_commits', 'files_count']].corr().round(2)
    fig_corr = px.imshow(corr,
                        title='Correlation Between Metrics',
                        text_auto=True,
                        color_continuous_scale='Blues')
    
    cur.close()
    conn.close()
    
    return fig_commits, fig_files, fig_box, fig_violin, fig_lang_heatmap, fig_corr

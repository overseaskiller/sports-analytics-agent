import math
import streamlit as st
import pandas as pd

st.set_page_config(page_title='Sports Analytics Agent', page_icon='🏀', layout='wide')
st.title('🏀🏈 Sports Analytics Agent — Prototype v1')
st.caption('NBA + NFL | Free | Manual historical game logs | No live odds or guaranteed predictions')
league=st.selectbox('League',['NBA','NFL'])
st.write('Upload a CSV of historical player game logs. Required columns: player, date, stat, value. Optional: team, opponent, game_id.')
file=st.file_uploader('Game logs CSV',type='csv')
if file:
    df=pd.read_csv(file)
    required={'player','date','stat','value'}
    if not required.issubset(df.columns):
        st.error('Missing columns: '+', '.join(sorted(required-set(df.columns))))
        st.stop()
    df['date']=pd.to_datetime(df['date'],errors='coerce')
    df['value']=pd.to_numeric(df['value'],errors='coerce')
    df=df.dropna(subset=['date','value']).sort_values('date')
    players=sorted(df.player.astype(str).unique())
    player=st.selectbox('Player',players)
    stats=sorted(df[df.player==player].stat.astype(str).unique())
    stat=st.selectbox('Stat',stats)
    line=st.number_input('Prop line',value=20.5,step=0.5)
    n=st.slider('Recent games',3,30,10)
    sub=df[(df.player==player)&(df.stat==stat)].tail(n)
    vals=sub.value
    if len(vals):
        over=int((vals>line).sum()); under=int((vals<line).sum()); pushes=int((vals==line).sum())
        a,b=over+1,len(vals)-over+1
        # Laplace smoothing; descriptive estimate, not calibrated forecast
        p=a/(a+b)
        c1,c2,c3=st.columns(3)
        c1.metric('Recent average',f'{vals.mean():.2f}')
        c2.metric('Over hits',f'{over}/{len(vals)}')
        c3.metric('Smoothed over rate',f'{p:.1%}')
        st.line_chart(sub.set_index('date')['value'])
        st.caption(f'Under: {under}, Pushes: {pushes}. Smoothed rate is a simple historical heuristic, NOT a validated probability or betting edge.')
        st.dataframe(sub,hide_index=True)
    st.subheader('Parlay workspace')
    if 'legs' not in st.session_state: st.session_state.legs=[]
    side=st.radio('Side',['Over','Under'],horizontal=True)
    if st.button('Add leg'):
        hits=over if side=='Over' else under
        estimate=(hits+1)/(len(vals)+2)
        st.session_state.legs.append({'league':league,'player':player,'stat':stat,'line':line,'side':side,'estimate':estimate})
    if st.session_state.legs:
        st.dataframe(pd.DataFrame(st.session_state.legs),hide_index=True)
        st.warning('Legs may be correlated. Multiplying hit rates would be misleading; no joint parlay probability is reported.')
        if st.button('Clear parlay'): st.session_state.legs=[]; st.rerun()
else:
    st.info('Start with the included sample CSV, then replace it with verified historical game logs.')
st.divider()
st.subheader('Agent instructions (ChatGPT mode)')
st.code('Analyze NBA and NFL player props from user-provided or verifiable current data. Show sample size, recent hit rates, averages, opponents and injury uncertainty. Never invent live odds, injuries, games, or probabilities. Flag correlated parlay legs. Do not call a historical hit rate a calibrated prediction. Ask for a CSV or reliable source when data is missing.',language='text')

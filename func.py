from astropy.io import fits
from astropy.timeseries import LombScargle
import plotly.express as px
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def dados(file):
    #importando os dados e retirando NaN
    data=fits.open(file)[1].data
    df=pd.DataFrame({'flux':list(data['FLUX']),'time':list(data['time'])})
    df2=df[df['time'].notna()]
    df2=df2[df2['flux'].notna()]
    
    # Normalizar o fluxo (subtrair a média)
    #fluxo_norm = df2['flux'] - df2['flux'].mean()
    fluxo_norm = df2['flux']
    
    # Duração
    duracao = df2['time'].max() - df2['time'].min()
    
    # Frequência mínima 
    fmin = 1.0 / (duracao*20)
    
    #Frequência máxima
    intervalo_medio = np.median(np.diff(df2['time']))
    fmax = 1.0 / (2.0 * intervalo_medio)
    
    # Número de frequências a testar
    n_freq = 100000
    
    # Calcular o periodograma
    frequencias = np.linspace(fmin, fmax, n_freq)
    potencia = LombScargle(df2['time'], fluxo_norm).power(frequencias)
    
    # Converter frequências para períodos (em dias)
    periodos = 1/ frequencias

    #Dataframe do periodograma
    periodograma=pd.DataFrame({'PSD (ppm².d)':potencia,'Period (Dias)':periodos,'Frequencia (1/d)':frequencias})
    periodograma['Frequencia (Hz)']=periodograma['Frequencia (1/d)']*1.1574074074*(10**(-5))
    periodograma['PSD (ppm²/Hz)']=periodograma['PSD (ppm².d)']/(1.1574074074*(10**(-5)))

    #picos principais
    picos_calc=periodograma.sort_values('PSD (ppm².d)',ascending=False,ignore_index=True)[0:5]
    picos_calc['Period (Dias)']=picos_calc['Period (Dias)'].round(2).apply(str)
    return(df,periodograma,picos_calc)

def figura(bruto,periodograma,picos_calc):
    # Criar figura com subplots
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=("Curva de Luz do Kepler", "Periodograma Proprio","Periodos Mais Intensos"),
        row_heights=[0.2, 0.4,0.4],
        vertical_spacing=0.11)
    
    #Ajuste de tamanho
    fig.update_layout(width=800, height=900)

    #Criação dos graficos
    fig1=px.scatter(bruto,y='flux',x='time')
    
    fig2=px.line(periodograma,y='PSD (ppm²/Hz)',x='Frequencia (Hz)',log_x=True,log_y=True)
    fig2.update_traces(line_color='black')
   
    fig3=px.bar(picos_calc,y='PSD (ppm².d)',x='Period (Dias)')
    
    
    
    #Adicionando os grafcos a figura principal
    for trace in fig1.data:
        fig.add_trace(trace,row=1,col=1)
    for trace in fig2.data:
        fig.add_trace(trace,row=2,col=1)
    for trace in fig3.data:
        fig.add_trace(trace,row=3,col=1)
    
    #Ajustes de design e escala log
    fig.update_xaxes(type='log',showline=True,mirror=True, linecolor="black", gridcolor="lightgray",title_text=periodograma.columns[3],row=2,col=1)
    fig.update_xaxes(showline=True,mirror=True, linecolor="black", gridcolor="lightgray",title_text=bruto.columns[0],row=1,col=1)
    fig.update_yaxes(showline=True,mirror=True, linecolor="black", gridcolor="lightgray",title_text=bruto.columns[1],row=1,col=1)
    fig.update_yaxes(type='log',showline=True,mirror=True, linecolor="black", gridcolor="lightgray",title_text=periodograma.columns[4],row=2,col=1)
    fig.update_xaxes(showline=True,mirror=True, linecolor="black", gridcolor="lightgray",title_text=picos_calc.columns[1],row=3,col=1)
    fig.update_yaxes(showline=True,mirror=True, linecolor="black", gridcolor="lightgray",title_text=picos_calc.columns[0],row=3,col=1)
    fig.update_layout(plot_bgcolor='white',paper_bgcolor='white')



    #Adição das linhas vermelhas verticais nos picos principais
    t='''shapes = []
    shapes.append(
        dict(
            type="line",
            xref=f"x2",
            yref=f"y2",
            x0=periodograma.loc[periodograma['PSD (ppm²/Hz)'].idxmax(),'Frequencia (Hz)'],
            y0=periodograma['PSD (ppm²/Hz)'].min(),
            x1=periodograma.loc[periodograma['PSD (ppm²/Hz)'].idxmax(),'Frequencia (Hz)'],
            y1=periodograma['PSD (ppm²/Hz)'].max(),
            line=dict(
                color="red",
                width=5,
                dash="dash",
            ),opacity=0.7,
            layer="above"
        )
    )'''
    k='''shapes.append(
        dict(
            type="line",
            xref=f"x3",
            yref=f"y3",
            x0=gab.loc[gab['Fluxo'].idxmax(),'Frequencia'],
            y0=gab['Fluxo'].min(),
            x1=gab.loc[gab['Fluxo'].idxmax(),'Frequencia'],
            y1=gab['Fluxo'].max(),
            line=dict(
                color="red",
                width=5,
                dash="dash",
            ),opacity=0.7,
            layer="above"
        )
    )'''
    fig.update_layout(template="plotly_white")

    fig.write_image("figura.svg")

    
    return fig
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os


def grafica_dispersion_valor_posicion(df_fifa):
    
    traduccion_posicion = {
        'Goalkeeper': 'Portero',
        'Defender': 'Defensa',
        'Midfielder': 'Mediocampista',
        'Forward': 'Delantero'
    }

    jugadores = df_fifa.groupby('player_id').agg({
        'player_name': 'first',              
        'position': 'first',                 
        'market_value_eur': 'first',         
        'tournament_rating': 'max',          
        'total_goals_tournament': 'max',     
        'total_minutes_tournament': 'max',   
    }).reset_index()  

    jugadores['position'] = jugadores['position'].map(traduccion_posicion)

    # Obtiene jugadores con al menos 90 minutos totales jugados en el torneo para asegurar clasificaciones representativas
    jugadores_filtrados = jugadores[jugadores['total_minutes_tournament'] >= 90].copy()
    
    jugadores_filtrados['log_market_value'] = np.log10(
        jugadores_filtrados['market_value_eur'].clip(lower=1e4)
    )
    
    posicion = ['Portero', 'Defensa', 'Mediocampista', 'Delantero']
    colores_posicion = sns.color_palette('Set2', n_colors=4)
    color_map = dict(zip(posicion, colores_posicion))

    fig1,ax1 = plt.subplots(figsize=(12, 7))
    # ciclo para pintar cada posicion con su color y tamaño de punto segun goles
    for pos in posicion:
        subset = jugadores_filtrados[jugadores_filtrados['position'] == pos]
        ax1.scatter(
            subset['log_market_value'],              
            subset['tournament_rating'],             
            s=subset['total_goals_tournament'] * 20, # mutiplica la cantidad de goles por 20 para aumentar el tamaño del punto (ajustable segun preferencia)
            c=[color_map[pos]],                      
            alpha=0.55,                              
            edgecolors='white',                      
            linewidth=0.3,                           
            label=pos                                
        )

    escala_valor = [1e5, 1e6, 1e7, 1e8, 2e8] 
    ax1.set_xticks(np.log10(escala_valor))
    ax1.set_xticklabels([f'{v/1e6:.0f}M' for v in escala_valor])

    ax1.set_xlabel('Valor de Mercado (Millones EUROS)')
    ax1.set_ylabel('Clasificación en el Torneo (0-10)')
    ax1.set_title('¿El Valor en el Mercado de un Jugador se Representa por su Posición?\n Valor de mercado vs Clasificación en el torneo, por posición (diametro = Nro de goles)', fontweight='bold')
    ax1.legend(title='Posición', loc='lower right', framealpha=0.9)
    ax1.set_ylim(0, 10.5)
    
    sns.despine()
    plt.tight_layout()
    plt.show()

def grafica_goles_equipo (df_fifa):

    goles_x_equipo = df_fifa.groupby('team')['goals'].sum().sort_values(ascending=False)
    top_15 = goles_x_equipo.head(15)
    norm = plt.Normalize(top_15.min(), top_15.max())
    # escala de colores de 0.35 y 0.65 para las barras, evitando tonos muy claros y manteniendo contraste con el fondo blanco.
    colores_barras = plt.cm.Blues(norm(top_15.values) * 0.65 + 0.35) 

    fig2, ax2 = plt.subplots(figsize=(10, 8))
    barras = ax2.barh(top_15.index[::-1], top_15.values[::-1], color=colores_barras[::-1])
    
    for barra, valor in zip(barras, top_15.values[::-1]):
        ax2.text(barra.get_width() + 1, barra.get_y() + barra.get_height() / 2,
                 f'{int(valor)}', va='center', fontweight='bold')
    
    ax2.set_xlabel('Cantidad de Goles Totales', fontweight='bold')
    ax2.set_title('Top 15 Equipos Goleadores Mundial FIFA World Cup 2026', fontweight='bold')
    sns.despine()
    plt.tight_layout()
    plt.show()


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, "data/")
    base = pd.read_csv(path + "fifa_world_cup_2026.csv",header=0,sep=",",decimal=".")

    print(base.info())

    ft = pd.DataFrame(base.isnull().sum()).reset_index()
    ft.columns = ["Variable","Faltantes"]
    ft["% Faltantes"] = ft["Faltantes"] * 100 / base.shape[0]

    formato = pd.DataFrame({'Variable': list(base.columns), 'Formato': base.dtypes })
    ft = pd.merge(ft,formato,on=["Variable"],how="left")
    ft.loc[ft["% Faltantes"]>0,]
    
    grafica_dispersion_valor_posicion(base)
    grafica_goles_equipo(base)
    

main()
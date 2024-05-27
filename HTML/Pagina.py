from dash import Dash, html, dcc, Output, Input
import plotly.graph_objs as go
import psycopg2
import pandas as pd
import webbrowser

try:
    # Establish connection to PostgreSQL database
    connection = psycopg2.connect(
        host='Localhost',
        user='postgres',
        password='123456789',
        database='Proyect',
        port='5432',
    )

    print("Conexión exitosa")
    cursor = connection.cursor()

    # SQL queries for different scenarios
    consult_escenario1 = '''
        with Team_Stats as (
            select p.Id_Team, t.Name as Team_Name, sum(p.Basket) as Total_Basket, sum(p.Point) as Total_Point
            from Participe as p
            inner join Team as t on p.Id_Team = t.Id
            inner join Match as m on m.Code = p.Code_Match 
            where m.Id_season = '36701'
            group by p.Id_Team, t.Name
        ),
        Ranked_Teams as (
            select Id_Team, Team_Name, Total_Basket, Total_Point,
                rank() over (order by Total_Basket desc, Total_Point desc) as Team_Rank
            from Team_Stats
        ) select Id_Team, Team_Name, Total_Basket, Total_Point
        from Ranked_Teams
        order by Total_Point desc;
    '''

    consult_escenario2 = '''
        with Team_Bounce_Sum as (
            select p.Id_Team, t.Name, sum(p.Bounce) as Total_Bounce
            from Participe as p
            inner join Team as t on p.Id_Team = t.Id
            group by p.Id_Team, t.Name
        ),
        Ranked_Teams as (
            select Id_Team, Name, Total_Bounce,
                rank() over (order by Total_Bounce desc) as Team_Rank
            from Team_Bounce_Sum
        ) select Id_Team, Name, Total_Bounce
        from Ranked_Teams
        order by Total_Bounce desc;
    '''

    consult_escenario3 = '''
        with Team_Point_Sum as (
            select p.Id_Team, t.Name, sum(p.Point) as Total_Point
            from Participe as p
            inner join Team as t on p.Id_Team = t.Id
            group by p.Id_Team, t.Name
        ),
        Ranked_Teams as (
            select Id_Team, Name, Total_Point,
                rank() over (order by Total_Point desc) as Team_Rank
            from Team_Point_Sum
        ) select Id_Team, Name, Total_Point
        from Team_Point_Sum
        order by Total_Point desc;
    '''

    consult_escenario4 = '''
        with Max_Stadium as (
            select p.Id, p.Stadium, count(p.Stadium) as Count_Stadium
            from Place as p
            inner join Happen as h on p.Id = h.Id_Place
            inner join Match as m on h.code_match = m.code
            group by p.Id, p.Stadium
        ),
        Ranked_Stadiums as (
            select Id, Stadium, Count_Stadium,
                rank() over (order by Count_Stadium desc) as Stadium_Rank
            from Max_Stadium
        ) select Id, Stadium, Count_Stadium
        from Max_Stadium
        order by Count_Stadium desc;
    '''
    consult_escenario5 = '''
        with tallest_player as( select t.Name as Team_Name, p.Name as Tallest_Player,p.Height as Player_Height
        from Team as t
        inner join (select Id_team, max(Height) as Max_Height
    	from Player
    	group by Id_team) as max_heights on t.Id = max_heights.Id_team
        inner join Player as p on (t.Id = p.Id_team and max_heights.Max_Height = p.Height)),
        Ranked_Heights as (
            select Team_Name, Tallest_Player,
                rank() over (order by Player_Height desc) as ranked_tallest
            from tallest_player
        ) select Team_Name, Tallest_Player, Player_Height
        from tallest_player
        order by player_height desc;'''
    consult_escenario6 = '''
        with weight_player as (select t.Name as Team_Name, p.Name as Heavist_Player,p.Weight as Player_Weight
        from Team as t
        inner join (select Id_team, max(Weight) as Max_Weight
    	from Player
    	group by Id_team) as max_weights on t.Id = max_weights.Id_team
        inner join Player as p on (t.Id = p.Id_team and max_weights.Max_Weight = p.Weight)),
        Ranked_Weight as (
            select Team_Name, Heavist_Player,
                rank() over (order by Player_Weight desc) as ranked_weight
            from weight_player
        ) select Team_Name, Heavist_Player, Player_Weight
        from weight_player
        order by Player_Weight desc;    '''
    
    consult_escenario7 = '''with Younger_Player as (
        select t.Name as Team_Name, p.Name as Player_Name, p.Birthdate as Born, (current_date - p.Birthdate)/365 as Age
        from Player as p
        inner join Team as t on p.Id_Team = t.Id),
        Ranked_Players as (select Team_Name, Player_Name, Born, Age,rank() over (order by Age) as Player_Rank
                            from Younger_Player) select Team_Name, Player_Name, Born, Age
                            from Younger_Player
                            order by Born desc;'''
    
    consult_escenario8 = '''with Oldest_Player as (
        select t.Name as Team_Name, p.Name as Player_Name, p.Birthdate as Born, (current_date - p.Birthdate)/365 as Age
        from Player as p
        inner join Team as t on p.Id_Team = t.Id),
        Ranked_Players as (select Team_Name, Player_Name, Born, Age,rank() over (order by Age) as Player_Rank
        from Oldest_Player) 
        select Team_Name, Player_Name, Born, Age
        from Oldest_Player
        order by Born;'''
    
    consult_escenario9 = '''
            WITH Team_Wins_Count AS (
                SELECT 
                    t.Id AS Id_Team, 
                    t.Name AS Team_Name, 
                    t.Code_region, 
                    COUNT(*) AS Total_Wins
                FROM 
                    Match AS m
                INNER JOIN 
                    Participe AS p ON m.Code = p.Code_Match
                INNER JOIN 
                    Team AS t ON p.Id_Team = t.Id
                WHERE 
                    (m.Team1 = t.Id AND m.Result1 > m.Result2) OR 
                    (m.Team2 = t.Id AND m.Result2 > m.Result1)
                GROUP BY 
                    t.Id, t.Name, t.Code_region
            ),
            Ranked_Wins AS (
                SELECT 
                    twc.Code_region, 
                    twc.Team_Name, 
                    twc.Total_Wins,
                    ROW_NUMBER() OVER (PARTITION BY twc.Code_region ORDER BY twc.Total_Wins DESC) AS Wins_Rank
                FROM 
                    Team_Wins_Count twc
            )
            SELECT 
                r.Name AS Region_Name, 
                rw.Team_Name, 
                rw.Total_Wins
            FROM 
                Ranked_Wins rw
            INNER JOIN 
                Region r ON rw.Code_region = r.Code
            WHERE 
                rw.Wins_Rank = 1  -- Filtramos solo el equipo con la mayor cantidad de partidos ganados por región
            ORDER BY 
                rw.Code_region;'''
    

    consult_escenario10 = '''
            with Matches_Per_Day as (
            select p.Date as Dates, count(distinct m.Code) as Num_Matches
            from Match as m
            join Participe as p on m.Code = p.Code_Match
            group by Dates
        ),
        Ranked_Matches as (
            select Dates, Num_Matches,
                rank() over (order by Num_Matches) as Match_Rank
            from Matches_Per_Day
        ) select Dates, Num_Matches
        from Matches_Per_Day
        order by Num_Matches desc;'''
    


    colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightsteelblue', 'lightyellow', 'lightpink', 'lightslategray']

    
    # Execute queries and create DataFrames
    cursor.execute(consult_escenario1)
    rows_team1 = cursor.fetchall()
    df_team1 = pd.DataFrame(rows_team1, columns=['Id_Team', 'Team_Name', 'Total_Basket', 'Total_Point'])

    cursor.execute(consult_escenario2)
    rows_team2 = cursor.fetchall()
    df_team2 = pd.DataFrame(rows_team2, columns=['Id_Team', 'Name', 'Total_Bounce'])

    cursor.execute(consult_escenario3)
    rows_team3 = cursor.fetchall()
    df_team3 = pd.DataFrame(rows_team3, columns=['Id_Team', 'Name', 'Total_Point'])

    cursor.execute(consult_escenario4)
    rows_team4 = cursor.fetchall()
    df_team4 = pd.DataFrame(rows_team4, columns=['Id', 'Stadium', 'Count_Stadium'])

    cursor.execute(consult_escenario5)
    rows_team5 = cursor.fetchall()
    df_team5 = pd.DataFrame(rows_team5 , columns=['Team Name' , 'Tallest Player' , 'Player Height'])

    cursor.execute(consult_escenario6)
    rows_team6 = cursor.fetchall()
    df_team6 = pd.DataFrame(rows_team6 , columns=['Team Name' , 'Heavist Player' , 'Player Weight'])

    cursor.execute(consult_escenario7)
    rows_team7 = cursor.fetchall()
    df_team7 = pd.DataFrame(rows_team7 , columns=['Team Name' , 'Younger Player' , 'Born','Player Age'])

    cursor.execute(consult_escenario8)
    rows_team8 = cursor.fetchall()
    df_team8 = pd.DataFrame(rows_team8, columns=['Team Name' , 'Oldest Player' , 'Born','Player Age'])

    cursor.execute(consult_escenario9)
    rows_team9 = cursor.fetchall()
    df_team9 = pd.DataFrame(rows_team9, columns=['Region Name' , 'Team Name' , 'Total Wins'])

    cursor.execute(consult_escenario10)
    rows_team10 = cursor.fetchall()
    df_team10 = pd.DataFrame(rows_team10, columns=['Date' , 'Matches Number'])


    # Dash application setup
    app = Dash(__name__)

    app.layout = html.Div(style={'fontFamily': 'Georgia, serif' ''',
                                 'backgroundImage': 'url("/assets/foto1.png")',
                                 'backgroundSize': 'cover',
                                 'backgroundRepeat': 'no-repeat',
                                 'backgroundPosition': 'auto' '''},
                          children=[
                          # Logo
                          html.Img(src='/assets/logo_gameverse.png', style={'position': 'absolute', 'top': '10px', 'left': '40px', 'height': '70px', 'width': 'auto'}),
                          html.Img(src='/assets/gameverse.png', style={'position': 'absolute', 'top': '20px', 'left': '118px', 'height': '50px', 'width': 'auto'}),
                          # Barra de Navegacion
                          html.Div(style={'display': 'flex', 'justifyContent': 'flex-end', 'marginTop': '30px'}, children=[
                              html.Nav(style={'backgroundColor': 'white', 'padding': '1rem'}, children=[
                                  html.A('INICIO', href='/inicio', style={'color': 'black', 'marginRight': '1rem', 'textDecoration': 'none'}),
                                  html.A('ESCENARIOS', href='/escenarios', style={'color': 'black', 'marginRight': '1rem', 'textDecoration': 'none'}),
                                  html.A('CONCLUSION', href='/conclusion', style={'color': 'black', 'marginRight': '1rem', 'textDecoration': 'none'}),
                                  html.A('EQUIPO', href='/equipo', style={'color': 'black', 'marginRight': '1rem', 'textDecoration': 'none'})
                              ])
                          ]),

                            # Linea Naranja
                            html.Hr(style={'borderTop': '2px solid orange', 'margin': '0'}),
                        
                            dcc.Location(id='url', refresh=False),
                            html.Div(id='page-content', style={'padding': '2rem'})
                      ])
        

    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')]
    )
    def display_page(pathname):
        if pathname == '/escenarios':
            return html.Div([
                # Texto
                html.H2('1° Escenario:', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                dcc.Graph(
                    id='Escenario-1',
                    figure={
                        'data': [
                            go.Bar(x=df_team1['Team_Name'], y=df_team1['Total_Point'], name='Total Points'),
                            go.Bar(x=df_team1['Team_Name'], y=df_team1['Total_Basket'], name='Total Baskets')
                        ],
                        'layout': go.Layout(
                            barmode='group',
                            title={'text': 'Predecir el equipo ganador de la NBA, tomando como referencia los datos de la postemporada.', 'font': {'family': 'Georgia, serif', 'color': 'black'}},
                            xaxis={'title': 'Team'},
                            yaxis={'title': 'Count'}
                        )
                    }
                ),
                # Analisis
                html.H2('Análisis', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P("Se planteó el uso de un diagrama de barra, donde se muestra un potencial equipo ganador de la NBA con respecto a los 29 equipos restantes por medio de la comparación de las cestas y los puntos de la postemporada en donde se reducen a pocos equipos el ganador, encontrados en la base de datos.",
                        style={'fontFamily': 'Georgia, serif'}),
                #Discusiones
                html.H2('Discusiones', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                
                html.P('María Lucía Mendoza Gómez',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("Se puede apreciar en el diagrama que Indiana Pacers supera en cestas y puntos a los demás equipos como a los knicks y Cavaliers por muy poco, una posible desventaja sería el hecho de que no muestra interacciones o dinámicas de juego al querer conocer más acerca de los datos de la base de la NBA, pero esto no es mucho inconveniente dado que los diagramas permiten hacer una comparación clara y directa entre los puntos y cestas entre equipos y así poder visualizar al posible ganador de la NBA.",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Nicolás David González Pinzón',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P(" A lo largo de esta temporada de la NBA, se ha evidenciado el esfuerzo de todos los equipos por conseguir la victoria, pero lastimosamente sólo un equipo puede ser el ganador, y según las predicciones que se han hecho con las gráficas, puntajes y habilidades de cada equipo, se llegó a la conclusión de que el equipo que va a ganar esta versión de la NBA son los: Indiana Pacers.",
                        style={'fontFamily': 'Georgia, serif'}),
                
                html.P('Samuel Hernando Flores Villarreal',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("Para predecir al ganador de esta temporada de la NBA, se evalúa la cantidad de rebotes y de cestas que ha realizado cada equipo durante la temporada. A pesar de que esto es algo impredecible, debido a que en este deporte ocurren muchos giros inesperados, se considera que el equipo ganador de la NBA son los: Indiana Pacers",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Ana Camila Gomez',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("A lo largo de esta temporada de la NBA, se ha evidenciado el esfuerzo de todos los equipos por conseguir la victoria, pero lastimosamente sólo un equipo puede ser el ganador, y según las predicciones que se han hecho con las gráficas, puntajes y habilidades de cada equipo, se llegó a la conclusión de que el equipo que va a ganar esta versión de la NBA son los: Indiana Pacers.",
                        style={'fontFamily': 'Georgia, serif'}),

                # Linea Naranja
                html.Hr(style={'borderTop': '2px solid orange', 'margin': '0'}),
                
                # Texto
                html.H2('2° Escenario:', style={'color': 'BLACK', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                dcc.Graph(
                    id='Escenario-2',
                    figure={
                        'data': [
                            go.Bar(
                                x=df_team2['Name'], 
                                y=df_team2['Total_Bounce'], 
                                name='Total Bounces',
                                marker=dict(color='purple')  # Cambia 'blue' por cualquier color que prefieras
                            )
                        ],
                        'layout': go.Layout(
                            barmode='group', 
                            title={
                                'text': 'El equipo con mayor número de rebotes.', 
                                'font': {'family': 'Georgia, serif', 'color': 'black'}
                            },
                            xaxis={'title': 'Team'},
                            yaxis={'title': 'Count'}
                        )
                    }
                ),
                # Analisis
                html.H2('Análisis', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P("Se planteó el uso de un diagrama de barra, donde se muestra al equipo con el mayor número de rebotes, lo cual indica para la NBA una mayor posibilidad de cestas para el equipo destacado.",
                        style={'fontFamily': 'Georgia, serif'}),
                # Discusiones
                html.H2('Discusiones', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P('María Lucía Mendoza Gómez',style={'fontFamily': 'Georgia, serif'}),
                html.P("En los diagramas se muestra al equipo con el mayor número de rebotes que es Boston Celtics superando a los Knicks por una diferencia de 95 rebotes, en donde el gráfico facilita la comparación directa entre equipos en términos de rebotes, gracias a que es fácil de entender y rápido de interpretar, pero una desventaja es que no muestra los cambios con respecto a los rebotes con respecto a las temporada para poder ver el avance de los equipos y del equipo con mayor rebotes.",
                        style={'fontFamily': 'Georgia, serif'}),
                
                html.P('Nicolás David González Pinzón',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("El equipo con mayor número de rebotes, según la gráfica, son los …, lo que significa que aquellos jugadores han tenido más destreza y habilidades de juego, e indicios de encestar el balón en los diferentes partidos jugados.",
                        style={'fontFamily': 'Georgia, serif'}),
                
                html.P('Samuel Hernando Flores Villarreal',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("La gráfica proporciona una visión del rendimiento del equipo en varios aspectos del juego, incluyendo la defensa, el ataque, el control del ritmo y la contribución individual de los jugadores. Esto puede ser útil para evaluar el desempeño del equipo, identificar áreas de mejora y tomar decisiones estratégicas para el éxito futuro.",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Ana Camila Gomez',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("Boston Celtics lidera en rebotes, siendo el equipo con la mayor cantidad de rebotes totales, lo cual es un indicio de su fuerte presencia en el juego defensivo y su capacidad para recuperar balones. En general, la mayoría de los equipos tienen cantidades de rebotes similares, lo que sugiere una competencia pareja en términos de recuperación del balón. Los equipos que más destacan en rendimiento en rebotes son New York Knicks, Denver Nuggets y Cleveland Cavaliers. Por otro lado, los equipos con menor rendimiento en rebotes son Washington Wizards, Charlotte Hornets y Portland Trail Blazers. Este bajo rendimiento en rebotes totales podría explicarse por el hecho de que algunos equipos no clasificaron a los playoffs, por lo que tienen menos datos.",
                        style={'fontFamily': 'Georgia, serif'}),
                
                # Linea Naranja
                html.Hr(style={'borderTop': '2px solid orange', 'margin': '0'}),

                #Texto
                html.H2('3° Escenario:', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                dcc.Graph(
                    id='Escenario-3',
                    figure={
                        'data': [
                            go.Bar(x=df_team3['Name'], y=df_team3['Total_Point'], name='Total Points', marker = dict(color = 'red'))
                        ],
                        'layout': go.Layout(
                            barmode='group', 
                            title={'text': 'El equipo que más puntos logró.', 'font': {'family': 'Georgia, serif', 'color': 'black'}},
                            xaxis={'title': 'Team'},
                            yaxis={'title': 'Count'}
                        )
                    }
                ),
                # Analisis
                html.H2('Análisis', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P("Se planteó el uso del diagrama de barras, en donde se muestra al equipo que tiene mayor puntos de la base de la NBA, fundamental para evaluar el posible ganador de la NBA.",
                        style={'fontFamily': 'Georgia, serif'}),
                # Discusiones
                html.H2('Discusiones', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P('María Lucía Mendoza Gómez',style={'fontFamily': 'Georgia, serif'}),
                html.P("Los diagramas muestran de manera sencilla los puntos logrados por cada equipo y al equipo que tiene mayor puntos de la base de la NBA el cual es los Pacers sobre los Celtics por 336 puntos de diferencia, además de permitir ver los valores exactos de cada equipo por medio de las barras y la desventaja que logro identificar es que no se refleja cómo los puntos se distribuyeron a lo largo de los juegos por medio de las cestas",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Nicolás David González Pinzón',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("El equipo que ha anotado la mayor cantidad de puntos a lo largo de esta versión de la NBA, según la gráfica, ha sido el equipo de los Pacers quienes demuestran tener una ofensiva potente, equilibrada y eficiente, así como la capacidad para adaptarse a diferentes situaciones de juego. Esto puede ser un indicador importante de su éxito y competencia en la liga.",
                        style={'fontFamily': 'Georgia, serif'}),
                
                html.P('Samuel Hernando Flores Villarreal',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("Un estimado de los puntos realizados por el equipo que más puntos ha conseguido a lo largo de esta fase de la NBA, es el equipo Pacers con un total de 12.029 puntos, con datos obtenidos de la gráfica, demostrando así, grandes habilidades de juego, buen desempeño en la cancha y trabajo en equipo de todos sus participantes, ideales para un posible ganador.",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Ana Camila Gomez',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("Indiana Pacers lidera en puntos. Este equipo tiene la mayor cantidad de puntos totales, indicando una ofensiva muy efectiva y destacada en la liga. La mayoría de los equipos tienen cantidades de puntos bastante similares, lo que sugiere una competencia estrecha en términos de anotación. No hay una gran disparidad entre los equipos en la parte superior de la gráfica. Los equipos con mayor rendimiento ofensivo son Boston Celtics, Oklahoma City Thunder, Los Angeles Lakers y Milwaukee Bucks. Los equipos con menor rendimiento en puntos son Charlotte Hornets, Memphis Grizzlies, Brooklyn Nets y Portland Trail Blazers. Es probable que los equipos con menor cantidad de puntos totales no hayan avanzado a los playoffs, lo que podría explicar su men",
                        style={'fontFamily': 'Georgia, serif'}),
                
                
                # Linea Naranja
                html.Hr(style={'borderTop': '2px solid orange', 'margin': '0'}),

                html.H2('4° Escenario:', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                dcc.Graph(
                    id='Escenario-4',
                    figure={
                        'data': [
                            go.Bar(x=df_team4['Stadium'], y=df_team4['Count_Stadium'], name='Count Stadiums',marker = dict(color='grey'))
                        ],
                        'layout': go.Layout(
                            barmode='group', 
                            title={'text': ' En qué estadio se repiten más partidos', 'font': {'family': 'Georgia, serif', 'color': 'black'}},
                            xaxis={'title': 'Stadium'},
                            yaxis={'title': 'Count'}
                        )
                    }
                ),
                # Analisis
                html.H2('Análisis', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P("Se planteó el uso del diagrama de barras donde se identifica el estadio que ha sido sede de la mayor cantidad de partidos. Este análisis es útil para entender la popularidad y la capacidad de los estadios para albergar eventos deportivos.",
                        style={'fontFamily': 'Georgia, serif'}),
                # Discusiones
                html.H2('Discusiones', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P('María Lucía Mendoza Gómez',style={'fontFamily': 'Georgia, serif'}),
                html.P("En el diagrama se identifica por medio de las barras la cantidad de partidos jugados en cada estadio, en donde se puede visualizar de manera clara el estadio que ha sido sede de la mayor cantidad de partidos que es el Cripto.com Arena, donde se realizaron 91 partidos y una desventaja es que no se proporciona información sobre la calidad de los partidos o asistencia.",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Nicolás David González Pinzón',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("En la gráfica se ve que el estadio más concurrido, ha sido Crypto.com Arena, ubicado en Los Angeles, CA y correspondiente al equipo de los Clippers, con un total de 91 participaciones en aquella cancha, dando lugar a que quienes han sido mayormente anfitriones de partidos en múltiples ocasiones, son los Clippers.",
                        style={'fontFamily': 'Georgia, serif'}),
                
                html.P('Samuel Hernando Flores Villarreal',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("El hecho de que el estadio más visitado sea el Crypto.com Arena, según la gráfica, puede ser considerado como un lugar bastante popular y/o importante para llevar a cabo los partidos de la NBA, aportando así, fama también al equipo al cual le corresponde ese estadio, y esos son los Clippers.",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Ana Camila Gomez',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("El estadio donde hubo más partidos fue el Crypto.com Arena. En general, los otros estadios mantuvieron un nivel casi igual en la cantidad de partidos. Estadios como Acrisure Arena, Arena CDMX y Stan Sheriff Center tuvieron la menor cantidad de partidos. Tal vez esto se deba a la fase regular de la NBA.",
                        style={'fontFamily': 'Georgia, serif'}),
                
                # Linea Naranja
                html.Hr(style={'borderTop': '2px solid orange', 'margin': '0'}),

                html.H2('5° Escenario:', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                dcc.Graph(
                    id='Escenario-5',
                    figure={
                        'data': [
                            go.Bar(x=df_team5['Tallest Player'], y=df_team5['Player Height'], name='Team Name',marker = dict(color='green'))
                        ],
                        'layout': go.Layout(
                            barmode='group', 
                            title={'text': ' Los jugadores más altos de cada equipo', 'font': {'family': 'Georgia, serif', 'color': 'black'}},
                            xaxis={'title': 'Player'},
                            yaxis={'title': 'Height'}
                        )
                    }
                ),
                # Analisis
                html.H2('Análisis', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P("Se planteó el uso del diagrama de barras donde se identifica a los jugadores más altos de cada equipo, los cuales son útiles para jugar en la posición de poste y así lograr hacer jugadas cerca de la canasta a la defensiva u ofensiva y su posible estrategia de juego.",
                        style={'fontFamily': 'Georgia, serif'}),
                # Discusiones
                html.H2('Discusiones', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P('María Lucía Mendoza Gómez',style={'fontFamily': 'Georgia, serif'}),
                html.P("En los diagramas se identifica a los jugadores más altos de cada equipo, entre los cuales se destaca Victor Wembanyama con una altura de 223.52 cm, además de ofrecer un pequeño contexto sobre el impacto de la altura en el rendimiento del equipo el diagrama, aun así no muestran como la altura afecta el rendimiento en el juego lo cual es una desventaja.",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Nicolás David González Pinzón',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("Se sabe que hay personas altas, pero con los datos obtenidos en la gráfica, estos jugadores de la NBA, Victor Wembanayam , Boban Marjanovic y Bol Bol , en definitiva tienen una altura bastante descabellada, superando los dos metros con veinte centímetros, convirtiéndolos no sólo en los más altos de la NBA, sino en algunas de las personas más altas del mundo.",
                        style={'fontFamily': 'Georgia, serif'}),
                
                html.P('Samuel Hernando Flores Villarreal',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("Viendo las gráficas, se ve que los jugadores más altos, cuentan con un mejor rendimiento en la cancha, debido a la influencia que tienen en distintos aspectos, tales como, el dominio con el balón, una mejor defensa y ofensiva y, por supuesto la capacidad de salto al encestar el balón, ayudando significativamente con la estrategia del equipo.",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Ana Camila Gomez',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("Los jugadores más altos de cada equipo de la NBA son Victor Wembanyama y Boban Marjanović. En general, la estatura de los líderes de altura de cada equipo es bastante similar. Aunque la altura puede ofrecer ciertas ventajas en el juego, como el dominio en el rebote y la defensa, no garantiza el éxito por sí sola. Habilidades como el manejo del balón, el tiro preciso y la inteligencia en la cancha son cruciales para destacar en la liga, independientemente de la altura del jugador.",
                        style={'fontFamily': 'Georgia, serif'}),


                # Linea Naranja
                html.Hr(style={'borderTop': '2px solid orange', 'margin': '0'}),

                html.H2('6° Escenario:', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                dcc.Graph(
                    id='Escenario-6',
                    figure={
                        'data': [
                            go.Bar(x=df_team6['Heavist Player'], y=df_team6['Player Weight'], name='Team Name',marker = dict(color='gold'))
                        ],
                        'layout': go.Layout(
                            barmode='group', 
                            title={'text': 'Los jugadores más pesados de cada equipo', 'font': {'family': 'Georgia, serif', 'color': 'black'}},
                            xaxis={'title': 'Player'},
                            yaxis={'title': 'Weight'}
                        )
                    }
                ),
                # Analisis
                html.H2('Análisis', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P("Se planteó el uso del diagrama de barras donde se muestran a los jugadores más pesados, lo cual indica un gran potencial para jugadores en la defensa e impacto del juego para los equipos.",
                        style={'fontFamily': 'Georgia, serif'}),
                # Discusiones
                html.H2('Discusiones', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P('María Lucía Mendoza Gómez',style={'fontFamily': 'Georgia, serif'}),
                html.P("En el diagrama se muestran a los jugadores más pesados de cada equipo, entre ellos destacando Boban Marjanovic con un peso de 290 por medio de las barras y el juego con valores exactos, esto si lo comparamos con los resultados de los equipos se lograría ver de manera exitosa como el peso se relaciona con el desempeño, pero sin mostrar cómo el peso afecta o influye en el rendimiento del juego.",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Nicolás David González Pinzón',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("En muchos contextos, un mayor peso se asocia comúnmente con un rendimiento deportivo bajo. Sin embargo, en la NBA, el peso de los jugadores suele estar relacionado directamente con su altura. Esto significa que los jugadores más pesados, quienes son , según las gráficas; pueden contribuir a un mejor desempeño en la cancha, especialmente en la defensa.",
                        style={'fontFamily': 'Georgia, serif'}),
                
                html.P('Samuel Hernando Flores Villarreal',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("En el caso de uno de los jugadores más pesados, se ve que es uno de los más altos, y se está hablando de Boban Marjanović, quien comparte esa misma altura con Jusuf Nurkic, ambos miden nada más y nada menos que 2.24m, siendo los jugadores más altos de la NBA en la actualidad.",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Ana Camila Gomez',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("Los jugadores más pesados por equipo son Boban Marjanovic y Jusuf Nurkic. Sin embargo, el peso de los jugadores más pesados por equipo puede variar considerablemente. Por otro lado, los jugadores menos pesados son Richaun Holmes, Marvin Bagley y Eugene Omoruyi. Aunque el peso puede influir en el rendimiento en ciertos aspectos del juego, como la resistencia física y la capacidad para defender, no es el único factor determinante para el éxito en la liga.",
                        style={'fontFamily': 'Georgia, serif'}),

                
                # Linea Naranja
                html.Hr(style={'borderTop': '2px solid orange', 'margin': '0'}),

                html.H2('7° Escenario:', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                dcc.Graph(
                    id='Escenario-7',
                    figure={
                        'data': [
                            go.Bar(x=df_team7['Younger Player'], y=df_team7['Player Age'], name='Age',marker = dict(color='brown')),
                        ],
                        'layout': go.Layout(
                            barmode='group',
                            title={'text': ' El jugador más joven de la NBA', 'font': {'family': 'Georgia, serif', 'color': 'black'}},
                            xaxis={'title': 'Player'},
                            yaxis={'title': 'Age'}
                        )
                    }
                ),
                # Analisis
                html.H2('Análisis', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P("Se planteó el uso del diagrama de barras donde se muestra al jugador más joven de la NBA con el objetivo de exaltar su ingreso a tan poca edad a la NBA, que se traduce a un jugador con buen desarrollo desde temprana edad.",
                        style={'fontFamily': 'Georgia, serif'}),
                # Discusiones
                html.H2('Discusiones', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P('María Lucía Mendoza Gómez',style={'fontFamily': 'Georgia, serif'}),
                html.P("En el diagrama se logra comparar las edades de los jugadores y se logra identificar al jugador más joven de la NBA que es GG Jackson con una edad de 19 años al igual que otros jugadores, de manera fácil y rápida  con el objetivo de exaltar en la NBA ya sea por su posible desarrollo como jugador temprano, lo único sería que no se proporciona información sobre el rendimiento del jugador más joven en los juegos.",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Nicolás David González Pinzón',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("En la gráfica presenciamos que entre los 30 equipos hay 5 jugadores que tienen la misma edad (19 años), pero hablando más específicamente de quién es el jugador más joven en la actualidad de la NBA(quién fue el más reciente en nacer), en primer lugar estaría GG Jackson.",
                        style={'fontFamily': 'Georgia, serif'}),
                
                html.P('Samuel Hernando Flores Villarreal',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("Al analizar los datos representados en la gráfica, se llegó a la conclusión de que en la NBA actual, el jugador más joven es GG Jackson, con tan solo 19 años de edad, dando a entender que es un jugador bastante excepcional, encontrándose en un entorno altamente competitivo.",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Ana Camila Gomez',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("GG Jackson es el jugador por equipo más joven de la NBA. Su presencia en la liga representa un potencial de desarrollo significativo. Los jugadores jóvenes como él suelen recibir más tiempo de juego y oportunidades para crecer y mejorar sus habilidades en el campo. Sin embargo, también pueden enfrentar desafíos como la adaptación al ritmo y la intensidad del juego profesional, así como la gestión de expectativas y presión por parte de los aficionados y los medios de comunicación. En resumen, ser el jugador más joven en la NBA puede ser una señal de promesa y talento, pero también implica responsabilidades y desafíos únicos.",
                        style={'fontFamily': 'Georgia, serif'}),
                
                # Linea Naranja
                html.Hr(style={'borderTop': '2px solid orange', 'margin': '0'}),

                html.H2('8° Escenario:', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                dcc.Graph(
                    id='Escenario-8',
                    figure={
                        'data': [
                            go.Bar(x=df_team8['Oldest Player'], y=df_team8['Player Age'], name='Age',marker = dict(color='darkmagenta'))
                            ],
                        'layout': go.Layout(
                            barmode='group', 
                            title={'text': ' El jugador con mayor edad de la NBA', 'font': {'family': 'Georgia, serif', 'color': 'black'}},
                            xaxis={'title': 'Player'},
                            yaxis={'title': 'Age'}
                        )
                    }
                ),
                # Analisis
                html.H2('Análisis', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P("Se planteó el uso del diagrama de barras donde se identifica al jugador más veterano lo cual es útil para destacar al jugador con una larga trayectoria y experiencia en la liga de la NBA.",
                        style={'fontFamily': 'Georgia, serif'}),
                # Discusiones
                html.H2('Discusiones', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P('María Lucía Mendoza Gómez',style={'fontFamily': 'Georgia, serif'}),
                html.P("En el diagrama de barra se logra comparar las edades de los jugadores y se logra identificar al jugador más veterano de la NBA que es Lebron James, de manera fácil y rápida  con el objetivo de exaltar en la NBA ya sea por su gran trayectoría y  desarrollo como jugador, pero dado que los diagramas no proporcionan información sobre el rendimiento del jugador en los juegos causando un vacío.",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Nicolás David González Pinzón',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("Con la recopilación de datos de los 30 equipos en la gráfica, se presenta que el jugador con mayor edad de la NBA es Lebron James (con 39 años), quien juega en el equipo de los Lakers y actualmente es una leyenda del baloncesto.",
                        style={'fontFamily': 'Georgia, serif'}),
                
                html.P('Samuel Hernando Flores Villarreal',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("Lebron James, jugador del equipo de los Lakers en la NBA, es el jugador con mayor edad, ya que tiene 39 años, seguido de Jeff Green, quien también tiene la misma edad, convirtiéndolos en los jugadores con más experiencia de juego en la actual NBA.",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Ana Camila Gomez',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("LeBron James es el jugador más veterano de la NBA. Esto sugiere experiencia y liderazgo, pero también puede implicar desafíos físicos y la necesidad de adaptación para mantenerse competitivo.",
                        style={'fontFamily': 'Georgia, serif'}),
                
                # Linea Naranja
                html.Hr(style={'borderTop': '2px solid orange', 'margin': '0'}),

                html.H2('9° Escenario:', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                
                dcc.Graph(
                    id='Escenario-9',
                    figure={
                        'data': [
                            go.Bar(
                                x=df_team9['Team Name'], 
                                y=df_team9['Total Wins'], 
                                name='Region',
                                marker=dict(color=colors[:len(df_team9)])  # Asignar colores diferentes a cada barra
                            )
                        ],
                        'layout': go.Layout(
                            barmode='group',
                            title={'text': 'El equipo que más ha ganado partidos por región.', 'font': {'family': 'Georgia, serif', 'color': 'black'}},
                            xaxis={'title': 'Team Name'},
                            yaxis={'title': 'Total Wins'}
                        )
                    }
                ),
                # Analisis
                html.H2('Análisis', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P("Se planteó el uso del diagrama de barras donde se muestra el mayor número de equipos ganadores por regiones, donde el análisis permite comprender el equipo más exitoso en la liga de la NBA.",
                        style={'fontFamily': 'Georgia, serif'}),
                # Discusiones
                html.H2('Discusiones', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P('María Lucía Mendoza Gómez',style={'fontFamily': 'Georgia, serif'}),
                html.P("Por medio del diagrama se muestra el equipo con el mayor número de partidos ganados por región y los demás inferiores a este, logrando identificarse con facilidad lo cual permite comprender e identificar al equipo con una mayor posibilidad dado su éxito y su región en la NBA. Una posible desventaja es que no es posible saber qué entrenamientos o distribución más específica geográfica causa el posicionamiento de los equipos. ",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Nicolás David González Pinzón',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("El hecho de que el equipo Boston Celtics de la región Atlántico haya ganado más partidos que los demás equipos de su misma y de otras regiones, puede ser indicativo de un ambiente deportivo bien desarrollado y una formación de alta calidad. Esto demuestra la importancia de diversos factores que contribuyen al éxito del equipo.",
                        style={'fontFamily': 'Georgia, serif'}),
                
                html.P('Samuel Hernando Flores Villarreal',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("Básicamente, lo que dice la gráfica es que los Boston Celtics son un equipo con un gran talento local, entorno competitivo y estrategias de juego. Esto puede ser útil para comprender los factores que contribuyen al éxito deportivo en la región Atlántico y para identificar áreas de oportunidad para el desarrollo deportivo en otras áreas.",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Ana Camila Gomez',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("La gráfica indica que Boston Celtics tiene más victorias por región en la NBA, mostrando un patrón de éxito en esa área. Esto sugiere posibles diferencias en el rendimiento de los equipos en diversas regiones, que podrían estar influenciadas por factores como la calidad del equipo o el estilo de juego.",
                        style={'fontFamily': 'Georgia, serif'}),
                
                # Linea Naranja
                html.Hr(style={'borderTop': '2px solid orange', 'margin': '0'}),

                html.H2('10° Escenario:', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                dcc.Graph(
                    id='Escenario-10',
                    figure={
                        'data': [
                            go.Bar(x=df_team10['Date'], y=df_team10['Matches Number'], name='Matches', marker=dict(color = 'darkblue'))
                        ],
                        'layout': go.Layout(
                            title={'text': '¿Qué día se jugaron más partidos en la NBA?', 'font': {'family': 'Georgia, serif', 'color': 'black'}},
                            xaxis={
                                'title': 'Date',
                                'tickangle': -45,
                                'titlefont': {'size': 14},
                                'tickfont': {'size': 10}
                            },
                            yaxis={'title': 'Matches', 'titlefont': {'size': 14}, 'tickfont': {'size': 10}},
                            margin={'l': 50, 'r': 50, 't': 50, 'b': 100},
                            bargap=0.2,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)'
                        )
                    }
                ),
                # Analisis
                html.H2('Análisis', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P("Se planteó el uso del diagrama de barras donde se muestran los días en los cuales se jugaron la mayor cantidad de partidos e identificando el día con la mayor actividad en la NBA.",
                        style={'fontFamily': 'Georgia, serif'}),
                # Discusiones
                html.H2('Discusiones', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                html.P('María Lucía Mendoza Gómez',style={'fontFamily': 'Georgia, serif'}),
                html.P("En los diagramas se muestran el número de partidos jugados cada día y además se logra identificar los días en los cuales se jugaron la mayor cantidad de partidos e identificando el día con la mayor actividad en la NBA o patrones y tendencias en la programación de partidos, entre los cuales se encuentra el 12 de abril y el 14 de abril con 15 partidos realizados en cada uno. Aun así una desventaja notable es la falta de información sobre los resultados de los partidos.",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Nicolás David González Pinzón',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("La gráfica muestra que donde más partidos se llevaron a cabo, corresponden a los días en que la temporada regular finalizó, dándole paso al inicio de la postemporada, consiguiendo un total de 15 partidos diarios, es decir, la participación de todos los equipos de la NBA.",
                        style={'fontFamily': 'Georgia, serif'}),
                
                html.P('Samuel Hernando Flores Villarreal',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P(" Los dos días en donde se jugaron más partidos, fueron cruciales en esta etapa de la NBA, ya que en aquellos enfrentamientos se realizó la selección de los equipos que avanzaron a la postemporada (Playoff) y, por consiguiente, la eliminación de los equipos que no lo lograron. Lo cual fue concebido los días , según los datos obtenidos de la gráfica.",
                        style={'fontFamily': 'Georgia, serif'}),

                html.P('Ana Camila Gomez',style={'color': 'black','fontFamily': 'Georgia, serif'}),
                html.P("El día en el que se jugaron más partidos fue el 14 de abril, lo que sugiere que la NBA estaba en la fase final de la temporada regular. Esto implica que los equipos estaban compitiendo por asegurar sus posiciones en la tabla antes de los playoffs.",
                        style={'fontFamily': 'Georgia, serif'}),
                
                # Linea Naranja
                html.Hr(style={'borderTop': '2px solid orange', 'margin': '0'}),

            ])
        elif pathname == '/conclusion':
            return html.Div([
                html.Div(style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center'}, children=[
                html.Img(src='/assets/foto5.png', style={'width': '50%', 'height': 'auto'}),
                html.Div([
                    html.H2('María Lucía Mendoza Gómez', style={'color': 'black', 'padding': '1rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                    html.P("""Este proyecto fue el resultado de un extenso trabajo que involucró múltiples secuencias y análisis de datos. Desde el principio, la creación del modelo entidad-relacional y el modelo relacional fue un proceso complejo que requirió más tiempo del anticipado. Esta etapa incluyó la normalización y mejora de los modelos, asegurando la correcta definición de las llaves primarias y foráneas, así como la identificación de nuevas entidades, relaciones y atributos necesarios. Además, seleccionamos cuidadosamente los datos más relevantes de la página de la NBA, entre una amplia variedad de opciones disponibles.
                            La carga masiva de datos fue otro desafío significativo, ya que demandó más de cinco días de inserción manual continua, sumando cerca de 6.000 tuplas. Aunque algunas de estas tuplas se obtuvieron mediante funciones automatizadas, la mayoría requirió inserción manual, lo que implicó revisiones dobles para asegurar la precisión de los datos.
                            La creación de escenarios y la generación de diagramas y gráficos en Python usando Dash y la librería ‘Psycopg2’ también presentó dificultades técnicas, ya que la importación de la librería no fue posible en muchos equipos. Sin embargo, esto me permitió profundizar en el curso de Ingeniería de Datos, analizando y resolviendo los escenarios propuestos.
                            A pesar de los desafíos, disfruté mucho del proyecto, especialmente debido al tema elegido por el grupo. Decidimos titularlo "Gameverse" en honor a la NBA, lo que nos permitió salir de nuestra zona de confort y explorar nuevas áreas de conocimiento.
                            En resumen, este proyecto integró todo el temario del curso y me introdujo en la creación de bases de datos, proporcionándome herramientas fundamentales para futuros proyectos. Por lo cual, estoy satisfecha con el resultado y el aprendizaje obtenido a lo largo del proceso.
                            """
                           , style={'fontFamily': 'Georgia, serif', 'marginLeft': '20px'}), 
                    html.H2('Ana Camila Gómez Hernández', style={'color': 'black', 'padding': '1rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                    html.P('''Una conclusión que se puede extraer es que hay una variedad de factores que contribuyen al rendimiento de los equipos en la NBA, incluyendo la capacidad ofensiva, la presencia defensiva, la altura y el peso de los jugadores, así como la distribución de partidos en diferentes estadios. Equipos como Indiana Pacers y Boston Celtics destacan en puntos y rebotes respectivamente, lo que indica fortalezas en diferentes aspectos del juego. Además, la distribución de partidos en diferentes estadios sugiere que algunos pueden tener más eventos que otros, lo que puede influir en la experiencia de los aficionados y en la preparación de los equipos. En general, estos datos proporcionan una visión amplia de la dinámica competitiva de la NBA y los diversos factores que contribuyen al éxito de los equipos.''', style={'fontFamily': 'Georgia, serif', 'marginLeft': '20px'}),
                    html.H2('Samuel Hernando Flores Villarreal', style={'color': 'black', 'padding': '1rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                    html.P('''El proyecto Gameverse ha sido un proyecto emocionante que nos llevó desde el mundo de la NBA hasta la creación de un videojuego. Nos sumergimos en la creación de una base de datos completa sobre la NBA, un proceso que implicó días de búsqueda, aprendizaje autónomo y la orientación de diversos profesores en diferentes áreas.
                            \n Con los datos recopilados, nos aventuramos en el desarrollo del juego utilizando herramientas como Ursina, subprocess y webbrowser. Esta combinación nos permitió crear una experiencia de juego que recrea un estadio de baloncesto al aire libre, así como utilizar aplicaciones para generar objetos en 3D y darle un realismo impresionante en tercera persona.
                            \n La base de datos sobre la NBA fue crucial en este proceso, ya que nos proporcionó la información necesaria para desarrollar diferentes escenarios y, especialmente, predecir al ganador futuro de la temporada 23-24 de la NBA. Desde las estadísticas de los jugadores hasta los detalles sobre equipos y partidos, cada elemento de la base de datos contribuyó al desarrollo de los diferentes escenarios y sirvió como inspiración para el diseño del videojuego.''', style={'fontFamily': 'Georgia, serif', 'marginLeft': '20px'}),
                    html.H2('Nicolás David González Pinzón', style={'color': 'black', 'padding': '1rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                    html.P('''Este proyecto sobre la NBA ha abarcado un análisis integral de jugadores, equipos, entrenadores, temporadas, partidos, lugares y regiones, utilizando diversas herramientas tecnológicas para gestionar y visualizar los datos. A través de la carga masiva de datos en SQL y su representación gráfica en Python, se han extraído insights clave que fueron recopilados en una página HTML, lo cual fue un trabajo que requirió de bastante dedicación y compromiso. Este proyecto no solo ha permitido una comprensión detallada del panorama actual de la NBA, sino que también ha demostrado la capacidad de las herramientas de análisis de datos para proporcionar información valiosa y predicciones informadas. La combinación de SQL para la gestión de datos, Python para la visualización y HTML para la presentación ha sido crucial para lograr estos resultados. Dando como resultado un proyecto bastante elaborado y completo, en el cual podamos predecir el equipo ganador de esta fase de la NBA.''', style={'fontFamily': 'Georgia, serif', 'marginLeft': '20px'})
                ])
                ])

            ])

        elif pathname == '/inicio' or pathname == '/':
            return html.Div([
                # Imagen Principal
                html.Div(style={'display': 'flex', 'justifyContent': 'center'}, children=[
                html.Img(src='/assets/foto1.png', style={'width': 'auto', 'height': 'auto'})]),

                # Linea Naranja
                html.Hr(style={'borderTop': '2px solid orange', 'margin': '0'}),
                # Texto
                html.H2('¿De qué trata?', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),

                html.P("""El proyecto se enfoca en la National Basketball Association (NBA), la principal liga privada de baloncesto profesional de Estados Unidos, establecida en 1949 tras la fusión de la National Basketball League y la Basketball Association of America. 
                        La temporada 2023-2024 de la NBA comenzó el 5 de octubre de 2023 con la pretemporada, contando inicialmente con 30 equipos. La temporada regular arrancó el 24 de octubre de 2023 y concluyó el domingo 14 de abril de 2024. La postemporada comenzó el sábado 20 de abril de 2024, culminando con las Finales de la NBA alrededor del 23-24 de junio de 2024. 
                        Cada día, entre 2 y 4 equipos participan en 1 o 2 partidos, avanzando solo los ganadores a las siguientes etapas de la competición.""",
                        style={'fontFamily': 'Georgia, serif'}),
                        
                html.H2('¿Problematica?', style={'color': 'black', 'padding': '0rem', 'minHeight': '0px', 'fontFamily': 'Georgia, serif'}),
                
                html.P("""Al iniciar este proyecto, la NBA se encuentra en la fase final de la postemporada, que finaliza alrededor del 23-24 de junio de 2024. El objetivo principal es aprovechar los datos disponibles desde el 5 de octubre de 2023 y aplicar los conocimientos adquiridos en ingeniería de datos para recopilar información relevante 
                       sobre los equipos y sus estadísticas durante la temporada. Con esta información, se busca predecir al equipo ganador de la NBA basándose en el desempeño histórico y actual de los equipos en la liga.""",
                       style={'fontFamily': 'Georgia, serif'}),

            ])
        elif pathname == '/equipo':
            return html.Div([
                html.Div(style={'display': 'flex', 'justifyContent': 'center'}, children=[
                    html.Img(src='/assets/N.png', style={'width': '25%', 'height': 'auto','marginRight': '1rem', 'marginLeft': '1rem'}),
                    html.Img(src='/assets/A.png', style={'width': '25%', 'height': 'auto','marginRight': '1rem'}),
                    html.Img(src='/assets/M.png', style={'width': '25%', 'height': 'auto','marginRight': '1rem'}),
                    html.Img(src='/assets/S.png', style={'width': '25%', 'height': 'auto'})
                ]),
                html.Div(style={'display': 'flex'}, children=[
                    html.P('Nicolás David González Pinzón',style={'color': 'black', 'padding': '1rem', 'marginLeft': '2rem'}),
                    html.P('Ana Camila Gómez Hernández',style={'color': 'black', 'padding': '1rem', 'marginLeft': '4rem'}),
                    html.P('María Lucía Mendoza Gómez',style={'color': 'black', 'padding': '1rem', 'marginLeft': '5rem'}),
                    html.P('Samuel Hernando Flores Villarreal',style={'color': 'black', 'padding': '1rem', 'marginLeft': '4rem'})
                ])
            ])
        else:
            return html.Div([
                html.H2('Página no encontrada', style={'color': 'white', 'padding': '1rem', 'minHeight': '200px'}),
                html.P('La página que buscas no existe.')
            ])


    if __name__ == '__main__':
        webbrowser.open('http://127.0.0.1:8050')
        app.run_server(debug = True)
        
except Exception as ex:
    print(ex)
finally:
    connection.close()
    print('Conexion finalizada')

def test_get_created():
    users = [
            {"username": "alvaro3", "password": "MILC(man,i love ceimaf)123", "e_mail": "a3@gmail.com"},
            {"username": "bruno3", "password": "h0la soy del Monse", "e_mail": "b3@gmail.com"},
            {"username": "leo3", "password": "Burrito21", "e_mail": "l3@gmail.com"},
    ]

    tokens = {}
    for u in users:
        response = cl.post(f"/users/{json_to_queryparams(u)}") 
        assert response.status_code == 200
        data = response.json()

        tokens[u["username"]] = data["token"]

    test_robots = [
            ("daneel R olivaw", tokens["leo3"], "identity.py", None, 201),
            ("R giskard", tokens["leo3"], "identity.py", None, 201),
            ("Marvin", tokens["bruno3"], "identity.py", None, 201),
            ("deep thought", tokens["alvaro3"], "identity.py", None, 201),
    ]


    for robot_name, token, code, avatar, expected_code in test_robots:
        files = []
        if code:
            files.append(("code", code))

        response = cl.post(f"/robots/?name={robot_name}", headers={"token": token}, files=files)

        assert response.status_code == expected_code

    test_matches = [
            (tokens["bruno3"], "partida0", "Marvin", 2, 4, 10000, 200, "algo", "Lobby",3, 201),
            (tokens["bruno3"], "partida1", "Marvin", 2, 4, 10000, 200, "algo", "InGame" , 3, 201),
            (tokens["leo3"], "partida2", "daneel R olivaw", 2, 4, 5000, 100, "algo", "Finished", 1, 201),
            (tokens["leo3"], "partida3", "R giskard", 3, 4, 8540, 2, "algo", "Lobby", 2, 201)
    ]

    for token, m_name, r_name, min_p, max_p, games, rounds, password, state, robot_id, expected_code in test_matches:

        response = cl.post(f"/matches/created", headers={"token": token},
                            json = {"name": m_name,"name_robot": r_name, "max_players": max_p,
                                "min_players": min_p, "rounds": rounds, "games": games,
                                "password": password,"state": state ,"robotId": robot_id})

        assert response.status_code == expected_code
    
    # forr a better test we would need the implementation of start endpoint
    test_get_matches = [(tokens["alvaro3"],[]),
                         (tokens["bruno3"], ["partida1"]),
                         (tokens["leo3"],["partida2"])]

    for token, names in test_get_matches:
        response = cl.get(f"/matches/iniciated", headers={"token": token})
        assert [d['name'] for d in response.json()] == names



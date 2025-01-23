def run_cypher(driver, query, parameters={}):
    with driver.session() as session:
        result = session.run(query, parameters)
        data = result.data()
        return data

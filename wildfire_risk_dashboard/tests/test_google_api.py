import ee

ee.Authenticate()
ee.Initialize(project='project-acf0062f-af6b-4917-944')
print(ee.String('Hello from the Earth Engine servers!').getInfo())
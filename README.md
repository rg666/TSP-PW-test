# TSP-PW-test
This is the solution for the problem statement given to solve the travelling salesman problem(TSP). Underlying library used for optimisation is from Google's Go-Tools(https://developers.google.com/optimization/).

Scope covered in the solution:

1. Randomly generate lat-long co-ordinates within (0,100) plane and calculate the optimal route for the number of points generation passed.
2. You may pass your own co-ordinates to the program and get the optimal route as well.
3. 2 APIs are hosted at /randomtsproute and /generatetsproute. When passed with correct input parameters, the optimal route calculation is passed as response.
4. Getting up and running script is master_build_and_run.sh, please execute it on your linux machine to install the program (P.S. I have used an Ubuntu VM).
5. A minimal test suite is created as a Postman test collection, which also includes testing comments to be found in the tests folder. Simply import it to Postman to test.

Technical implementation explanation:

The solution is containorised using docker. The solution is implemented using 3 containers/services: docker-rabbitmq-example-master, tsp_plotWise_backend and flask-app. 
Back end APIs are hosted using a minimal flask app, which in return calls tsp_plotWise_backend over rabbitmq AMQP protocol using RPC(to keep the session synchronous). The tsp_plotWise_backend service is the heart of the route optimisation of the app, which leverages on Google's Go-Tools.

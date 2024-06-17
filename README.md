
# Blockchain Tracker

Blockchain Tracker monitors the number of UserOperation Events on the Polygon Mainnet, segmented by duration (hour/day/week). The data is stored in a PostgreSQL database, which is hosted on [Neon](https://neon.tech/), and visualized using Grafana.

Biconomy Bundler addresses are imported from an ERC4337 CSV file into the database, enabling identification of from_to addresses that are part of the Biconomy Bundler addresses.

Data import processes are automated through GitHub Actions.


## Run Locally

Clone the project

```bash
  git clone https://github.com/mersihakaramustafic/blockchain-tracker.git
```

Go to the project directory

```bash
  cd blockchain-tracker
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the program

```bash
  python main.py
```


## Environment Variables

To run this project locally, you will need to add the following environment variables to your .env file:

`INFURA_API_KEY`

`PSQL_CONNECTION_STRING`

For the purpose of this project, I stored the environment variables in Github -> Settings -> Secrets and Variables, so Github Actions can be run.


## 🔗 Links
Grafana dashboard is public and can be accessed on the [link](https://karamustaficmersiha.grafana.net/public-dashboards/c8659b7db1ef43448166760a7d772d05?orgId=1&refresh=2h).
## License

[MIT](https://choosealicense.com/licenses/mit/)


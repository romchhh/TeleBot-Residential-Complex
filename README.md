# TeleBot-Residential-Complex

Welcome to TeleBot-Residential-Complex! This Telegram bot allows residents to submit various requests related to access control and security within the residential complex.

## Features
- **Request Submission**: Users can submit requests such as passing a pedestrian, passing a car, or calling security directly through the bot.
- **Admin Panel**: Administrators have access to an admin panel where they can manage requests, view statistics, and perform administrative tasks.
- **Web Interface**: Requests submitted through the bot are displayed on a local webpage for easy review by security personnel.

## Bot Abilities
- **Pass a Pedestrian**: Residents can request permission for pedestrians to enter the residential complex.
- **Pass a Car**: Residents can request permission for vehicles to enter the residential complex.
- **Call Security**: Residents can call for security assistance directly through the bot.

## Integration with FastAPI
The bot is integrated with a FastAPI-based web interface, providing additional functionality and ease of use. The web interface allows security personnel to view and manage requests submitted through the bot in real-time.

To run the web interface:
1. Install FastAPI and Uvicorn by running `pip install fastapi uvicorn`.
2. Navigate to the `Kursova_Telegram_Bot` directory.
3. Run the following command: `uvicorn TeleBot.server.server:app --log-level debug --port=8001`.
4. Access the web interface at the specified URL.

## Screenshots
![Request Submission](https://github.com/romchhh/TeleBot-Residential-Complex/assets/123520267/a7e25f4c-d33b-4933-8bce-8507aa1a160f)

![Web Interface](https://github.com/romchhh/TeleBot-Residential-Complex/assets/123520267/58ff8412-ed9f-471d-8b25-d2f32bd322de)

As you can see you can only open the local web page from admin panel in the bot (/admin):

![image](https://github.com/romchhh/TeleBot-Residential-Complex/assets/123520267/22abfae7-76a4-444e-b757-77476cfa4fc6)


![image](https://github.com/romchhh/TeleBot-Residential-Complex/assets/123520267/ba550702-9142-4035-8857-5aec3b2306d7)


And here you can see like new requests are looking like to security:

![image](https://github.com/romchhh/TeleBot-Residential-Complex/assets/123520267/28af14cf-a2da-4f35-b6a9-dd9d2a55e14e)




## Usage
1. **Start the Bot**: Users can start using the bot by sending a `/start` command.
2. **Submit Requests**: Users can submit requests by selecting appropriate options from the bot's menu.
3. **Admin Functions**: Administrators can access the admin panel by sending an `/admin` command. From there, they can manage requests and perform administrative tasks.

## Installation

1. Clone this repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Set up your Telegram bot token, group ID, admin IDs, and other configurations in the `config.py` file.

```python

token = "YOUR BOT TOKEN"
admins = (ADMIN IDS,)
group_id = GROUP ID FOR REQUEST
db_data_name = "PATH TO YOUR DB FILE"
URL_SITE = f'http://127.0.0.1:8001' # in index.html, app.js

```

5. Run the bot using `python main.py`.

## Contributing
Contributions are welcome! If you'd like to contribute to the project, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature-name`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Create a new pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For any questions or issues, please open an issue in the [issue tracker](https://github.com/your-username/telegram-marketplace-bot/issues).

## Roadmap

Future improvements and features planned for this project are listed in the [roadmap](ROADMAP.md) file.

## Acknowledgements

- Thanks to the developers of the [FastApi]([https://github.com/aiogram/aiogram](https://fastapi.tiangolo.com/)) library for making it easy to make a friendship between webpage and python.

## Contact

For any inquiries or feedback, please contact [Roman](mailto:roman.fedoniuk@gmail.com).

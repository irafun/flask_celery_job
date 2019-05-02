- Queue task is organized and executed by using Celery with rabbitmq server
- Sending email is executed using mailgun API
- There is an additional parameters that need to be filled, email_to: the recipient of where the email should be sent.
  String data type. So in total there are 5 fields need to be filled:
    1. event_id
    2. email_to
    3. email_subject
    4. email_content
    5. timestamp
- the timestamp field should be filled with standard JavaScript built-in JSON object, e.g "2019-05-01T18:25:43.511Z"
- there are an optional request header-required method using flask-jwt-extended library such as update(put) and delete,
  token obtained by first registering an user with a password, login using mentioned data,
  use the token obtained by adding phrase "Bearer " in the begining of request header token
- it is also provided any other method such as retrieve, put, and delete in both of users and emails endpoints
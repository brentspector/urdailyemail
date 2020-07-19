from urdailyemail import email


def lambda_function(event, context):
    return email.generate_email()

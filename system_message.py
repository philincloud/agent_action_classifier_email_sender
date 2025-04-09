import json



def system_message(addresses, actions):
   # retrieve the actions list from json file in the same directory

   with open(actions, 'r') as f:
    actions = json.load(f)
# Ensure actions is a list
   if not isinstance(actions, list):
    raise ValueError("actions must contain a JSON array")
   with open(addresses, 'r') as f:
    addresses = json.load(f)
# Ensure actions is a list
   if not isinstance(addresses, list):
    raise ValueError("addresses must contain a JSON array")
   system_message = (
        "You are a classifier that assigns a single address from this list: " +
        f"'{', '.join(addresses)}' " +
        "and single action from this list: " +
        f"'{', '.join(actions)}'. " +
        "Given a user prompt, please retrieve 4 informations from it: action and address from the list that best matches the prompt's meaning, also full message_text and message subject. If you can not see subject assign just 'message to {assigned address}'. If language is diffrent than english return 'unknow language'. Keep message unchanged but  cut of sentence including address " +
        "Please return response as JSON according to this format: " +
        '{"action": "{assigned action}","subject":"{assigned subject}", "address": "{assigned address}", "message_text": "{assigned message_text}"} ' +
        "Do not explain, just return the JSON. Here is an example of the prompt and expected output: " +
        "prompt: 'I want to send email to Daniel and the content is: Daniel. We need a report for tomorrow morning about last month transactions. Could you prepare it please? Thank you, With Regards, Philip.' " +
        "output: " +
        '{"action": "email", "address": "danielmogulecki@onet.pl","subject":"last month report", "message_text": "Daniel. We need a report for tomorrow morning about last month transactions. Could you prepare it please? Thank you, With Regards, Philip."}' +
        ""
    )

   return system_message
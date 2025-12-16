UNEXPECTED_REQUEST = (
    'Unexpected error. If you have subscription issues, please contact support via the bot menu. Order number: '
)

SECOND_FAILURE = (
    '❌ Payment failed for the second time. Subscription has been canceled. You have been removed from the chat and channel'
)

REMOVED = (
    '❌ Subscription was canceled in the WayForPay personal account. You have been removed from the chat and channel'
)

REFUND = (
    '❌ Payment was refunded. Subscription has been canceled. You have been removed from the chat and channel'
)

DECLINED = '❌ Payment failed. Please try again'

SUSPENDED = (
    '❌ Subscription was suspended in the WayForPay personal account. You have been removed from the chat and channel. '
    'If you want to renew the subscription, please purchase it again via the bot'
)

EXPIRED = '❌ Payment failed. Payment time has expired. Please try again'

IN_PROGRESS = (
    '❌ Payment is stuck on the payment system side. If funds are charged, please cancel the subscription in the '
    'WayForPay personal account and contact support via the bot menu. Order number: '
)

FIRST_FAILURE = (
    '❌ Payment could not be charged. A retry payment will be created tomorrow. '
    'If the second payment also fails, you will be removed from the chat and channel'
)

UNSUB = (
    '✅ Successfully unsubscribed from recurring payments. You have been removed from the chat and channel'
)

SUB_ABSENT = '❌ You do not have an active subscription'

NOT_ACTIVE_KICK = (
    'The payment system reported an inactive recurring payment status. '
    'You have been removed from the chat and channel'
)

FIRST_MESSAGE = '''
Hi!

This is a bot for accessing Telegram channel. Here you can purchase a subscription, check its status,
find answers to frequently asked questions, or contact support.

After purchasing a subscription, you will automatically receive an invitation to the private channel.
The subscription lasts for one month or six months — whichever is more convenient for you.

Payments are charged automatically, and you will receive a reminder 3 days before the next charge.
'''

BUY_SUBSCRIPTION = (
    'After payment, you will receive access to the channel. To purchase a subscription, follow this link:\n{}'
)

FAQ = '''
1. How long does the subscription last?
One or six months — depending on the selected package.

2. How does payment work?
Through a payment system. The next payment is automatic — the bot will remind you 3 days in advance.

3. How do I unsubscribe?
Just write “I want to unsubscribe” to the bot — and we will take care of everything.
'''

SUCCESS_PAYMENT = 'Payment was successful ✅'

LINK_CHAT = (
    'Here is your link to the private chat {}\nPlease note that the link is valid for one hour'
)

LINK_CHANNEL = (
    'And the link to the private channel {}\nIt is also valid for one hour'
)

ZOOM_LINK = (
    'Meditation recording:\n{}\n🧷 Access code: <code>{}</code>'
)

PAYMENT_IN_3_DAYS = '⏳ Hi! There are 3 days left until the next payment!'

PAYMENT_ERROR = '❌ Error while creating the payment.'

ACTIVE_SUBSCRIPTION = (
    '✅ Your subscription is active. Next charge date: {}'
)

BROADCAST = 'Saved. Send the text in the next message'

BROADCAST_SENT = '✅ Text has been sent to all users: {}'

SUBSCRIPTION_NAME = 'Channel Subscription'

HELP_TEXT = 'Please describe the problem in detail. '

MENU = 'Main menu'

CHOOSE_FREQ = 'choose billing frequency:'

PRODUCT_COST = '{}\n\n{}\n\nPrice: {} EUR'

ORDER_INFO = 'Name: {}\nDescription: {}\nLink: {}'

SHOW_INVOICE = (
    'payment invoice:\n\n{}\n\nafter payment, the product link will be sent in the bot'
)

ORDER_LIST = 'here is the list of your products:'

UNSUB_OR_CHECK_STATUS_MENU = (
    'in this menu you can unsubscribe or check the status of your subscription'
)

BUY_SUB_MENU = (
    'in this menu you can purchase a subscription to Alena’s private channel and chat'
)

QUESTION_LIST = 'list of frequently asked questions'

HOW_TO_PAY_ANSWER = (
    'Choose the product you want to purchase, follow the link and select a convenient payment method — '
    'Apple Pay, Google Pay, or card. The system will handle everything and send the product link here in the bot. '
    'If you cannot pay via the link, please contact support.'
)

RECORD_ANSWER = (
    'Of course :) The recording will be sent here the day after the live session.'
)

RECEIVE_PRODUCT_ANSWER = (
    'You will receive a message in the bot with the link immediately after payment. '
    'If it doesn’t arrive but the payment was successful — please contact us, something may have gone wrong.'
)

IF_NOT_ACCESS_ANSWER = (
    'Very easy — click “unsubscribe” and subscribe again. This way the system will update your card details.'
)

SUPPORT_ANSWER = 'Click “need help” in the main menu'

SUPPORT_RECEIVED_QUESTION = (
    'Thank you. Support has received your request and will respond shortly in the bot.'
)

INACTIVE_CHAT = 'chat is inactive'

NEW_CHAT = '📩 new request from {} | @{}\n\n{}'

NO_ADMIN_TAKE = (
    'At the moment, support has not taken your request yet.\n\n'
    'As soon as support starts working on it, you will be able to add more details.'
)

USER_SENT = '👤 User {}: {}'

ADMIN_JOIN = (
    'You have joined the chat. All your messages will now be sent to the user {}'
)

ADMIN_SENT = '‍💻 Admin: {}'

ADMIN_CONFIRM = 'sent {}'

PAUSE_CHAT = (
    'Chat with {} has been paused. Your messages will no longer be sent to the user. '
    'Their messages will still be delivered to you.'
)

USER_CLOSED_CHAT = 'support chat has been closed'

ADMIN_CLOSED_CHAT = 'chat closed ✅'

WRITE_PRODUCT_PRICE = 'enter the price in EUR'

WRITE_PRODUCT_NAME = 'saved ✅ Now enter the product name'

WRITE_PRODUCT_DESCR = 'saved ✅️ Now enter the product description'

WRITE_PRODUCT_LINK = (
    'saved ✅️ now enter the link\n\n'
    'if you enter `.`, the user will receive '
    '`the link in the bot 30 minutes before the start`'
)

PRODUCT_SAVED = (
    '✅ product saved! It is now visible to users\n\n'
    'name: {}\nprice: {} EUR\ndescription: {}\nlink: {}'
)

PRODUCT_LIST = 'product list:\n\n'

PRODUCT_ITEM = 'ID: {}, name: {}, price: {}, link: {}'

WRITE_PRODUCT_ID = 'enter the product ID'

MUST_BE_INT = 'must be a number, try again'

WRITE_EDIT_FIELD = (
    'saved ✅️ now enter the field you want to change (field name exactly as shown in the product list)'
)

WRITE_NEW_VALUE = 'saved ✅️ now enter the new value for this field'

EDIT_SUCCESS = (
    'field {} successfully updated to {} for ID {} ✅️'
)

WRITE_PRODUCT_ID_TO_BROADCAST = (
    'enter the product ID whose owners should receive the broadcast. '
    "'enter '-' to send the broadcast to ALL users'"
)

WRITE_DATE_TO_BROADCAST = (
    'saved. Send the date in the next message\n'
    'format: YYYY-MM-DD HH:MM\n'
    "Send '-' to send the message immediately"
)

WRONG_DATE_FORMAT = 'invalid date format. Use YYYY-MM-DD HH:MM'

CONFIRM_DATE_BROADCAST = (
    "schedule the message: '{}' for {}? yes/no"
)

YES = 'yes'
NO = 'no'

BROADCAST_PLANNED = 'message scheduled for {}'

BROADCAST_CANCELED = 'scheduling canceled'

YES_OR_NO = 'please answer yes or no'

CHOOSE_CATEGORY = (
    'choose a category (1, 2, 3, or 4)\n\n'
    '1. current\n'
    '2. webinar recordings\n'
    '3. school and others\n'
    '4. archive'
)

MUST_BE_CATEGORY = 'must be 1, 2, 3, or 4, try again'

PRODUCT_MOVED = (
    'product with ID `{}` has been moved to category {}'
)

NEW_CHAT_RECEIVED = '📩 request from {}'

NO_CHATS = 'no requests available'

ALL_ORDERS = (
    '\n\n User: {}  |  Product: {}  |  Date: {}  |  WFP: {}'
)

NO_ORDERS = 'no purchases found'

WRITE_PRODUCT_ID_REMOVE = 'enter the ID of the product you want to delete'

PRODUCT_REMOVED = 'product with ID `{}` has been deleted ✅'

LINK_WILL_BE_LATER = 'the link will be sent to the bot 30 minutes before the start'

PRODUCT_LINK = 'product link:\n{}'

PRODUCT_SUCCESS_PAYMENT = 'successful payment!\n\n{}'

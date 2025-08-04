# Dead Man's Switch Support Guide

## Service overview
Dead Man's Switch is an automated email service that sends pre-written messages to specified recipients if the user stops responding to periodic check-in notifications. It functions as an "electronic will" for important messages users want delivered if they become incapacitated.

## How it works
1. Users write emails and specify recipients
2. The system sends check-in notifications at set intervals
3. If the user clicks the check-in link, the timer resets
4. If the user misses all notifications, messages are automatically sent

## Understanding intervals
Intervals control when notifications are sent and when messages are delivered. They appear as comma-separated numbers (e.g., "1,2" or "30,45,52,60").

### How intervals work
- **All numbers except the last** = notification days
- **Last number** = message send day

**Example**: Interval "1,2,3"
- Day 1 after last check-in: notification sent
- Day 2 after last check-in: notification sent
- Day 3 after last check-in: messages sent (no notification)

**Example**: Interval "30,45,52,60"
- Days 30, 45, 52: notifications sent
- Day 60: messages sent

### Multiple messages interaction
When you have multiple messages with different intervals:
- You receive ONE notification per day if ANY message requires it
- The notification covers all messages scheduled for that day
- One check-in resets the timer for ALL messages

**Example**:
- Message A: "7,14,30"
- Message B: "10,20,30"
- Message C: "7,30"

You'll get notifications on days 7, 10, 14, and 20 (not multiple on day 7 or 30)

### Interval rules
- Numbers don't need to be sequential (e.g., "30,60,100" is valid)
- Free accounts: Fixed at "1,2" (shown in dropdown, not changeable)
- Premium accounts: Custom intervals via text field

## Account types

### Free account
- 1 message maximum
- 1 recipient per message (own email only - trial mode)
- Fixed interval: "1,2" (notification day 1, send day 2)

### Premium account ($50 lifetime or subscription)
- 100 messages maximum
- 100 recipients per message
- Custom intervals per message
- No fair use limits

## Key features

### Check-in methods
- **Email** (default): Automatic for all accounts
- **Telegram**: Set up via Settings page
- **Browser push notifications**: Set up via Settings page
- **Android app**: Sends notifications and allows one-tap check-in (no iOS app available)

### Default intervals (premium)
The system suggests "30,45,52,60" by default, meaning:
- Check-ins requested 30, 45, and 52 days after last activity
- Messages sent on day 60 if no response

### Postponement feature
- Delays don't change interval numbers
- System treats the last postponement day as a check-in
- Intervals resume counting from that date

**Example**: With "1,2,3" intervals and 10-day postponement:
- Days 1-10: no notifications (dormant)
- Day 11: first notification (1 day after postponement ends)
- Day 12: second notification
- Day 13: messages sent

## Message management

### Creating messages
- Text-only (no attachments currently)
- Each message is independent with its own:
  - Recipients (up to 100 for premium)
  - Subject line
  - Body text
  - Intervals (premium only)

### Disabling/enabling messages
If messages are accidentally sent:
1. They appear as "disabled" in the account
2. To re-enable: change interval from "disabled" back to numbers (e.g., "1,2,3")
3. Messages remain visible but inactive while disabled

## Account management

### Password recovery
Users click "Forgot my password" to receive a recovery email

### Data security
- Messages transferred via TLS
- Stored privately on servers (not encrypted at rest)
- Not accessed by staff

### Payment methods
- **Lifetime premium**: Bitcoin or credit card
- **Subscription**: Credit card only

## Common support scenarios

### "I'm not getting any notifications"
This is usually because messages were accidentally sent and are now disabled:
1. Direct user to the **Log tab** to check their activity history
2. Look for when messages were sent
3. Check if messages show as "disabled" in their account
4. To fix: change intervals from "disabled" back to numbers (e.g., "1,2,3")

### "I have multiple messages but only got one notification"
This is correct behaviour. You receive ONE notification per day when ANY message needs it. All messages share the same check-in system.

### "What do the numbers mean?"
Explain that all numbers except the last are notification days. The last number is when messages are sent.

### "My messages were sent by mistake"
Check if messages show as "disabled". Guide them to re-enable by setting intervals back from "disabled" to their preferred numbers.

### "I want different timing for different messages"
Confirm they have premium. Each message can have completely different intervals.

### "I'm going on holiday for 2 weeks"
Show postponement feature. Their switch will be dormant for 14 days, then intervals resume.

### "Can I skip days in my intervals?"
Yes, premium users can use any numbers (e.g., "7,30,60" to get notified weekly, then monthly, then send at 60 days).

### "How many notifications can I set?"
No practical limit on notifications - just list all days before the final send day.

## Quick reference

### Free account intervals
- Cannot be changed: "1,2"
- Notification: 1 day after last check-in
- Send: 2 days after last check-in
- Recipients: Self only (registered email address)

### Premium custom intervals
- Format: comma-separated numbers in text field
- Example: "7,14,21,30" = notifications on days 7, 14, 21; send on day 30
- Each message can have different intervals

### Log tab
- Shows complete activity history
- Displays when user checked in
- Shows when messages were sent
- Essential for troubleshooting notification issues

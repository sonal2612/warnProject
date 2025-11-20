import os
from app import app, mail
from flask_mail import Message

print("=" * 60)
print("🧪 WARRN Email Configuration Test")
print("=" * 60)

with app.app_context():
    # Check configuration
    print(f"\n📧 Email Configuration:")
    print(f"   Server: {app.config.get('MAIL_SERVER')}")
    print(f"   Port: {app.config.get('MAIL_PORT')}")
    print(f"   Username: {app.config.get('MAIL_USERNAME') or '❌ NOT SET'}")
    print(f"   Password: {'✅ SET' if app.config.get('MAIL_PASSWORD') else '❌ NOT SET'}")
    
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        print("\n❌ ERROR: MAIL_USERNAME or MAIL_PASSWORD not configured!")
        print("\nTo fix this, run:")
        print('   $env:MAIL_USERNAME="your-email@gmail.com"')
        print('   $env:MAIL_PASSWORD="your-app-password"')
        print("\nSee EMAIL_SETUP_GUIDE.md for detailed instructions.")
    else:
        print("\n📤 Sending test email...")
        try:
            msg = Message(
                subject='🧪 WARRN Email Configuration Test',
                sender=app.config['MAIL_USERNAME'],
                recipients=[app.config['MAIL_USERNAME']]
            )
            msg.body = """This is a test email from WARRN.

If you receive this email, your email configuration is working correctly! ✅

You can now receive notifications when new animal incidents are reported.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WARRN - Wildlife Animal Rescue & Response Network
"""
            mail.send(msg)
            print("✅ SUCCESS! Test email sent successfully!")
            print(f"   Check your inbox: {app.config['MAIL_USERNAME']}")
            print("   (Don't forget to check spam/junk folder)")
        except Exception as e:
            print(f"❌ FAILED! Error sending email:")
            print(f"   {str(e)}")
            print("\n💡 Common fixes:")
            print("   1. Make sure you're using an App Password (not regular password)")
            print("   2. Enable 2-Factor Authentication on Gmail")
            print("   3. Generate new App Password at: https://myaccount.google.com/apppasswords")
            print("   4. Remove any spaces from the app password")

print("\n" + "=" * 60)

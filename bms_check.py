# Author: Dedeepya Bonthu <dedeepya.bonthu@gmail.com>
# Date:  2016-09-21

"""
Notifies when the bookings for a movie on given date and venue(s) are open.

Requires:
Movie ID(can be optained from the url of movie page) Ex: ET00045462-MT
List of venue IDS(can be obtained from the url of venue page)
Ex: PVSF-MT,CPMH-MT
Date for which the booking has to be checked Ex: 20160921
"""

import argparse
import re
import smtplib
import urllib2
import urlparse
from bs4 import BeautifulSoup
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

APP_PASSWORD = 'jdvnhjfqosxeoqal'
EMAIL = 'dedeepya.bonthu@gmail.com'


def check_movie(movie_id, venue_ids, date):
    url = 'https://in.bookmyshow.com/hyderabad/movies/nowshowing'
    found_venues = []
    print 'Checking'

    movies_data = urllib2.urlopen(url).read()
    parsed_movies_data = BeautifulSoup(movies_data, 'html.parser')
    movie = None
    for book_button in parsed_movies_data.find_all(
            'section', {'class': 'language-based-formats'}):
        book_button = str(book_button)
        if re.search(movie_id, book_button):
            movie = re.match('.*href="(?P<booking_url>.*?)".*',
                             book_button, re.DOTALL)
            break

    if not movie:
        return

    print 'Found movie'

    booking_url = movie.group('booking_url')
    booking_url = urlparse.urljoin('https://in.bookmyshow.com', booking_url)
    booking_url = booking_url[:-9] + date

    venues_data = urllib2.urlopen(booking_url).read()
    parsed_data = BeautifulSoup(venues_data, 'html.parser')
    for venue in parsed_data.find_all('a', {'class': '__venue-name'}):
        for venue_id in venue_ids:
            if re.search(venue_id, str(venue)):
                found_venues.append(venue_id)

    if not found_venues:
        print 'No venues found'
        return

    from_addr = EMAIL
    to_addr = EMAIL
    subject = 'Bookmyshow tickets'
    body = 'Tickets open for {0} at {1} on {2}'.format(
        movie_id, found_venues, date)

    send_mail(from_addr, to_addr, APP_PASSWORD, subject, body)


def send_mail(from_addr, to_addr, password, subject, body):
    """Send mail to gmail account"""
    print 'Sending mail...'

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(from_addr, password)
    server.ehlo()
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject
    body = body
    msg.attach(MIMEText(body, 'plain'))
    text = msg.as_string()
    server.sendmail(from_addr, to_addr, text)


def main():
    parser = argparse.ArgumentParser(description='Tool to check if bookings \
are open', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    default_movie_id = 'ET00038693-MT'
    default_venue_ids = 'PVSF-MT,CPMH-MT,AGHM-MT'
    default_date = '20170429'
    parser.add_argument('--movie', action='store', help='ID of the movie',
                        dest='movie_id', default=default_movie_id)
    parser.add_argument('--venues', action='store', help='Name of the venue',
                        dest='venue_ids', default=default_venue_ids)
    parser.add_argument('--date', action='store', help='Date',
                        dest='date', default=default_date)

    arguments = parser.parse_args()
    movie_id = arguments.movie_id
    venue_ids = arguments.venue_ids.split(',')
    date = arguments.date

    check_movie(movie_id, venue_ids, date)


if __name__ == "__main__":
    main()

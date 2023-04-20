# Import modules to handle exceptions and transactions.

from unicodedata import name
from urllib import response
from django.test import TestCase
from django.urls import reverse
from .models import Video
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction



#test home title name
"""
Checks whether the title message "Travel Agency" is displayed on the home page.
"""

class TestHomePageMessage(TestCase):

    def test_app_title_message_shown_on_home_page(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, 'Travel Agency')



class TestAddVideos(TestCase):
    """
    The class contains three tests.
    1. Test the add_video_page function.
    2. Test the add_video_page function with a valid video.
    3. Test the add_video_page function with an invalid video.
    """
    
    def test_add_video(self):

        valid_video = {
            'name': 'London',
            'url': 'https://www.youtube.com/watch?v=45ETZ1xvHS0',
            'notes' : 'places and notes'
        }

        url = reverse('add_video')
        response = self.client.post(url, data=valid_video, follow=True)

        self.assertTemplateUsed('video_collection/video_list.html')

        #does the video list show the new video?
        self.assertContains(response, 'London')
        self.assertContains(response, 'places and notes')
        self.assertContains(response, 'https://www.youtube.com/watch?v=45ETZ1xvHS0')

        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        video = Video.objects.first()

        self.assertEqual('London', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=45ETZ1xvHS0', video.url)
        self.assertEqual('places and notes', video.notes)
        self.assertEqual('45ETZ1xvHS0', video.video_id)

    def test_add_video_invalid_url_not_added(self):

        invalid_video_urls = [
            'https://www.facebook.com/',
            'https://www.facebook.com/watch?',
            'https://www.apple.com/store?afid=p238%7CseIEs444j-dc_mtid_1870765e38482_pcrid_649686730713_pgrid_13945964887_pntwk_g_pchan__pexid__&cid=aos-us-kwgo-brand-apple--slid---product-',
            'https://music.youtube.com/watch?'

        ]

        for invalid_video_url in invalid_video_urls:
            
            new_video = {
                'name': 'example',
                'url': invalid_video_url,
                'notes' : 'example notes'
            }

            url = reverse('add_video')
            response = self.client.post(url, new_video)

            self.assertTemplateNotUsed('video_collection/add.html')

            messages = response.context['messages']
            message_texts = [ message.message for message in messages ]

            self.assertIn('Invalid Youtube URL', message_texts)
            self.assertIn('Please check the data entered.', message_texts)

            video_count = Video.objects.count()
            self.assertEqual(video_count, 0)



class TestVideoList(TestCase):
    """
    The class contains three tests.
    1: checks whether all videos are displayed on the video list page.
    2: checks whether the correct number of videos are displayed.
    3: Test_no_video_message: checks whether a message"No videos" is displayed when there are no videos in the video list.
    4: test_video_number_messages (from 1 to more videos )
    
    """
    
    def test_all_videos_displayed_in_correct_order(self):

        v1 = Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=124')
        v2 = Video.objects.create(name='ecf', notes='example', url='https://www.youtube.com/watch?v=123')
        v3 = Video.objects.create(name='dfg', notes='example', url='https://www.youtube.com/watch?v=122')
        v4 = Video.objects.create(name='tyu', notes='example', url='https://www.youtube.com/watch?v=121')

        expected_video_order = [ v3, v2, v4, v1]

        url = reverse('video_list')
        response = self.client.get(url)

        videos_in_template = list(response.context['videos'])

        self.assertEqual(videos_in_template, expected_video_order)

    def test_no_video_message(self):
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, 'No videos')
        self.assertEqual(0, len(response.context['videos']))

    def test_video_number_message_one_video(self):
        v1 = Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=124')
        url = reverse('video_list')
        response = self.client.get(url)

        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')

    def test_video_number_message_two_videos(self):
        v1 = Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=123')
        v1 = Video.objects.create(name='ZXY', notes='example', url='https://www.youtube.com/watch?v=125')

        url = reverse('video_list')
        response = self.client.get(url)

        self.assertContains(response, '2 videos')
  

class TestVideoSearch(TestCase):
    """
    Test the search functionality of the video list page.
    1: video_search_matches: test if the search term provided matches the video name and returns the expected video order.
    2: test_video_search_no_results: checks whether a message "No videos" is displayed when there are no videos in the video list.
    3: test_video_search_no_results_with_search_term: checks whether a message "No videos" is displayed when there are no videos in the video list and a search term is provided.

    """


    def test_video_search_matches(self):
        v1 = Video.objects.create(name='Another travel video name', notes='example', url='https://www.youtube.com/watch?v=2RakvEQhTTA&ab_channel=BookingHunterTV')
        v2 = Video.objects.create(name='another short video name', notes='example', url='https://www.youtube.com/watch?v=xy4e-R8FiR4')
        v3 = Video.objects.create(name='youtube!!!!!', notes='example', url='https://www.youtube.com/watch?v=od7F_hTlC1g')
        v4 = Video.objects.create(name='This one is different', notes='example', url='https://www.youtube.com/watch?v=NvUYUYNcaTE')
        expected_video_order = [v2, v1]

        response = self.client.get(reverse('video_list') + '?search_term=another')
        videos_in_template = list(response.context['videos'])

        self.assertEqual(videos_in_template, expected_video_order)

class TestVideoModel(TestCase):
    """
    tests if creating two videos with the same name and URL raises an IntegrityError. 
    The test creates one Video object, v1, and then tries to create another Video object with the same name and URL. 
    It asserts that an IntegrityError is raised.
    """
    
    def test_duplicate_video_raises_integrity_error(self):
        v1 = Video.objects.create(name='Another travel video name', notes='example', url='https://www.youtube.com/watch?v=2RakvEQhTTA&ab_channel=BookingHunterTV')
        with self.assertRaises(IntegrityError):
            Video.objects.create(name='Another travel video name', notes='example', url='https://www.youtube.com/watch?v=2RakvEQhTTA&ab_channel=BookingHunterTV')
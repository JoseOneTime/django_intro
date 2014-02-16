import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse

from polls.models import Poll

def create_poll(question, days):
	return Poll.objects.create(
		question=question,
		pub_date=timezone.now() + datetime.timedelta(days=days)
	)

class PollViewTests(TestCase):
	def test_index_view_with_no_polls(self):
		response = self.client.get(reverse('polls:index'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'No polls are available.')
		self.assertQuerysetEqual(response.context['latest_poll_list'], [])

	def test_index_view_with_a_past_poll(self):
		create_poll("Past poll", -30)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			response.context['latest_poll_list'],
			['<Poll: Past poll>']
		)

	def test_index_view_with_a_future_poll(self):
		create_poll("Future poll", 30)
		response = self.client.get(reverse('polls:index'))
		self.assertContains(response, 'No polls are available.', status_code=200)
		self.assertQuerysetEqual(response.context['latest_poll_list'], [])

	def test_index_view_with_future_poll_and_past_poll(self):
		create_poll("Past poll", -30)
		create_poll("Future poll", 30)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			response.context['latest_poll_list'],
			['<Poll: Past poll>']
		)

	def test_index_view_with_two_past_polls(self):
		create_poll('past poll 1', -30)
		create_poll('past poll 2', -5)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			response.context['latest_poll_list'],
			['<Poll: past poll 2>', '<Poll: past poll 1>']
		)


class PollIndexDetailTests(TestCase):
	def test_detail_view_with_a_future_poll(self):
		future_poll = create_poll("future poll", 5)
		response = self.client.get(reverse('polls:detail', args=(future_poll.id,)))
		self.assertEqual(response.status_code, 404)

	def test_detail_view_with_a_past_poll(self):
		past_poll = create_poll('past poll', -5)
		response = self.client.get(reverse('polls:detail', args=(past_poll.id,)))
		self.assertContains(response, past_poll.question, status_code=200)


class PollMethodTests(TestCase):

	def test_was_published_recently_with_future_poll(self):
		"""
		was_published_recently() should return False for polls whose
		pub_date is in the future 
		"""
		future_poll = Poll(pub_date=timezone.now() + datetime.timedelta(days=1))
		self.assertEqual(future_poll.was_published_recently(), False)

	def test_was_published_recently_with_old_poll(self):
		old_poll = Poll(pub_date=timezone.now() - datetime.timedelta(days=2))
		self.assertEqual(old_poll.was_published_recently(), False)

	def test_was_published_recently_with_recent_poll(self):
		recent_poll = Poll(pub_date=timezone.now() - datetime.timedelta(hours=23))
		self.assertEqual(recent_poll.was_published_recently(), True)

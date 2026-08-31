import pygame
import random
import time
from statistics import NormalDist
from data_manager import DataManager

class BriefStimulusDetectionTest:
	def __init__(self, screen, font):
		self.screen = screen
		self.font = font
		self.large_font = pygame.font.Font(None, 72)
		self.small_font = pygame.font.Font(None, 24)
		self.running = True

		self.WHITE = (255, 255, 255)
		self.BLACK = (0, 0, 0)
		self.BLUE = (70, 130, 180)
		self.BG = (128, 128, 128)

		# Two sequential blocks
		self.blocks = ['duration', 'hue']
		self.block_idx = 0

		# A quarter of the trials are blanks. Without them the staircase measures
		# willingness to say "yes", not detectability: saying yes to everything
		# drives it straight to the floor and scores as a perfect threshold.
		self.stim_trials_per_block = 30
		self.catch_trials_per_block = 10
		self.trials_per_block = self.stim_trials_per_block + self.catch_trials_per_block
		self.current_trial = 0
		self.results = []
		self.block_results = []
		self.schedule = []

		# Duration staircase: vary number of frames the stimulus is shown.
		# The fixed hue offset is deliberately low - at offset 40 a single frame
		# was trivially detectable and the staircase bottomed out immediately.
		self.dur_frames = 6
		self.dur_min = 1
		self.dur_max = 30
		self.dur_step = 1
		self.dur_fixed_hue = 18

		# Hue staircase: vary the red offset from the background gray.
		# Step size shrinks near the bottom so the staircase can settle.
		self.hue_offset = 50
		self.hue_min = 1
		self.hue_max = 120
		self.hue_fixed_frames = 2

		# 3-down-1-up staircase (converges to ~79% detection threshold)
		self.consecutive_correct = 0

		# State machine
		self.state = 'block_intro'
		self.state_start_time = time.time()
		self.stimulus_frames_shown = 0
		self.target_frames = 0
		self.stimulus_color = self.BG
		self.stimulus_present = True
		self.response_seen = False
		self.isi_duration = 0.0

	def _build_schedule(self):
		"""Shuffled list of per-trial stimulus-present flags for one block"""
		schedule = [True] * self.stim_trials_per_block + [False] * self.catch_trials_per_block
		random.shuffle(schedule)
		return schedule

	def _hue_step(self):
		"""Finer steps near the bottom of the range"""
		return 5 if self.hue_offset > 20 else 2

	def _stim_color(self):
		offset = self.dur_fixed_hue if self.blocks[self.block_idx] == 'duration' else self.hue_offset
		return (min(255, self.BG[0] + offset), self.BG[1], self.BG[2])

	def _target_frames(self):
		if self.blocks[self.block_idx] == 'duration':
			return self.dur_frames
		return self.hue_fixed_frames

	def _adjust_staircase(self, correct):
		"""3-down-1-up. Only stimulus-present trials move the staircase; catch
		trials say nothing about detectability, only about response bias."""
		block = self.blocks[self.block_idx]
		if correct:
			self.consecutive_correct += 1
			if self.consecutive_correct >= 3:
				self.consecutive_correct = 0
				if block == 'duration':
					self.dur_frames = max(self.dur_min, self.dur_frames - self.dur_step)
				else:
					self.hue_offset = max(self.hue_min, self.hue_offset - self._hue_step())
		else:
			self.consecutive_correct = 0
			if block == 'duration':
				self.dur_frames = min(self.dur_max, self.dur_frames + self.dur_step)
			else:
				self.hue_offset = min(self.hue_max, self.hue_offset + self._hue_step())

	def _start_trial(self):
		self.isi_duration = random.uniform(0.4, 0.9)
		self.stimulus_present = self.schedule[self.current_trial]
		self.state = 'isi'
		self.state_start_time = time.time()

	def _record_response(self, seen):
		rt = time.time() - self.state_start_time
		block = self.blocks[self.block_idx]

		trial_data = {
			'trial': self.current_trial + 1,
			'block': block,
			'stimulus_present': self.stimulus_present,
			'seen': seen,
			'correct': seen == self.stimulus_present,
			'rt_s': rt
		}
		if block == 'duration':
			trial_data['duration_ms'] = self.dur_frames * (1000.0 / 60.0)
			trial_data['at_floor'] = self.dur_frames <= self.dur_min
		else:
			trial_data['hue_offset'] = self.hue_offset
			trial_data['at_floor'] = self.hue_offset <= self.hue_min

		self.results.append(trial_data)
		self.block_results.append(trial_data)

		if self.stimulus_present:
			self._adjust_staircase(seen)

		self.response_seen = seen
		self.state = 'feedback'
		self.state_start_time = time.time()

	def run(self):
		clock = pygame.time.Clock()
		self.schedule = self._build_schedule()

		while self.running:
			current_time = time.time()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
					break
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						self.running = False
						break
					elif event.key == pygame.K_SPACE:
						if self.state == 'block_intro':
							self._start_trial()
						elif self.state == 'response':
							self._record_response(True)
						elif self.state == 'block_end':
							self.block_idx += 1
							if self.block_idx >= len(self.blocks):
								self.running = False
								break
							self.current_trial = 0
							self.block_results = []
							self.consecutive_correct = 0
							self.schedule = self._build_schedule()
							self.state = 'block_intro'
							self.state_start_time = current_time
					elif event.key == pygame.K_n:
						if self.state == 'response':
							self._record_response(False)

			if not self.running:
				break

			if self.state == 'isi':
				if current_time - self.state_start_time >= self.isi_duration:
					self.state = 'stimulus'
					self.state_start_time = current_time
					self.stimulus_frames_shown = 0
					self.target_frames = self._target_frames()
					self.stimulus_color = self._stim_color()

			elif self.state == 'stimulus':
				# Catch trials occupy the same frames, they just draw nothing
				self.stimulus_frames_shown += 1
				if self.stimulus_frames_shown >= self.target_frames:
					self.state = 'response'
					self.state_start_time = current_time

			elif self.state == 'response':
				if current_time - self.state_start_time >= 1.5:
					self._record_response(False)

			elif self.state == 'feedback':
				if current_time - self.state_start_time >= 0.4:
					self.current_trial += 1
					if self.current_trial >= self.trials_per_block:
						self.state = 'block_end'
						self.state_start_time = current_time
					else:
						self._start_trial()

			self.draw()
			pygame.display.flip()
			clock.tick(60)

		score = self.calculate_score()
		self.save_data(score)
		return score

	@staticmethod
	def _d_prime(hits, misses, false_alarms, correct_rejections):
		"""d' with the log-linear correction, so rates of 0 and 1 stay finite"""
		n_signal = hits + misses
		n_noise = false_alarms + correct_rejections
		if n_signal == 0 or n_noise == 0:
			return None
		hit_rate = (hits + 0.5) / (n_signal + 1)
		fa_rate = (false_alarms + 0.5) / (n_noise + 1)
		z = NormalDist().inv_cdf
		return z(hit_rate) - z(fa_rate)

	def calculate_score(self):
		if not self.results:
			return {}

		score = {'blocks': {}}
		for block in self.blocks:
			block_data = [r for r in self.results if r['block'] == block]
			if not block_data:
				continue

			signal = [r for r in block_data if r['stimulus_present']]
			noise = [r for r in block_data if not r['stimulus_present']]
			hits = sum(1 for r in signal if r['seen'])
			misses = len(signal) - hits
			false_alarms = sum(1 for r in noise if r['seen'])
			correct_rejections = len(noise) - false_alarms

			# Threshold from the tail of the staircase, stimulus-present trials only
			key = 'duration_ms' if block == 'duration' else 'hue_offset'
			unit = 'ms' if block == 'duration' else 'units'
			last_n = signal[-10:] if len(signal) >= 10 else signal
			threshold = sum(r[key] for r in last_n) / len(last_n) if last_n else None
			floor_pinned = sum(1 for r in last_n if r.get('at_floor'))

			score['blocks'][block] = {
				'estimated_threshold': threshold,
				'threshold_unit': unit,
				'n_trials': len(block_data),
				'n_signal_trials': len(signal),
				'n_catch_trials': len(noise),
				'hits': hits,
				'misses': misses,
				'false_alarms': false_alarms,
				'correct_rejections': correct_rejections,
				'hit_rate': hits / len(signal) if signal else None,
				'false_alarm_rate': false_alarms / len(noise) if noise else None,
				'd_prime': self._d_prime(hits, misses, false_alarms, correct_rejections),
				# A staircase sitting on its floor reports the floor value, not a
				# threshold - read it as a lower bound.
				'floor_pinned_trials': floor_pinned,
				'threshold_is_lower_bound': bool(last_n) and floor_pinned >= len(last_n) // 2,
				'trials': block_data
			}
		return score

	def save_data(self, score):
		if not score:
			return
		data = {'test_type': 'brief_stimulus_detection', **score}
		try:
			dm = DataManager()
			filepath = dm.save_test_data('brief_stimulus_detection', data)
			print(f"Brief Stimulus Detection data saved to {filepath}")
		except Exception as e:
			print(f"Error saving data: {e}")

	def draw(self):
		self.screen.fill(self.BG)

		center_x = self.screen.get_width() // 2
		center_y = self.screen.get_height() // 2

		block = self.blocks[self.block_idx] if self.block_idx < len(self.blocks) else 'done'

		title = self.font.render("Brief Stimulus Detection", True, self.WHITE)
		self.screen.blit(title, (20, 20))

		trial_label = self.small_font.render(
			f"Block: {block}  Trial: {self.current_trial + 1}/{self.trials_per_block}",
			True, self.WHITE
		)
		label_rect = trial_label.get_rect()
		label_rect.right = self.screen.get_width() - 20
		label_rect.y = 20
		self.screen.blit(trial_label, label_rect)

		def center_text(surf, y):
			r = surf.get_rect()
			r.center = (center_x, y)
			self.screen.blit(surf, r)

		if self.state == 'block_intro':
			if block == 'duration':
				lines = [
					"Block 1: Duration threshold",
					"A faint red-tinted patch may flash briefly.",
					"Some trials show nothing at all.",
					"Press SPACE if you saw it, N if you didn't.",
					"",
					"Press SPACE to begin."
				]
			else:
				lines = [
					"Block 2: Hue/contrast threshold",
					"A faint colored patch may flash for ~33ms.",
					"Some trials show nothing at all.",
					"Press SPACE if you saw it, N if you didn't.",
					"",
					"Press SPACE to begin."
				]
			for i, line in enumerate(lines):
				t = self.font.render(line, True, self.WHITE)
				center_text(t, center_y - 100 + i * 40)

		elif self.state in ('isi', 'response', 'stimulus'):
			pygame.draw.line(self.screen, self.WHITE, (center_x - 15, center_y), (center_x + 15, center_y), 2)
			pygame.draw.line(self.screen, self.WHITE, (center_x, center_y - 15), (center_x, center_y + 15), 2)

			if self.state == 'stimulus' and self.stimulus_present:
				sq = pygame.Rect(0, 0, 200, 200)
				sq.center = (center_x, center_y)
				pygame.draw.rect(self.screen, self.stimulus_color, sq)
			elif self.state == 'response':
				prompt = self.font.render("SPACE = saw it     N = didn't", True, self.WHITE)
				center_text(prompt, center_y + 80)

		elif self.state == 'feedback':
			# Neutral echo of the response - the participant is never told whether
			# they were right, and a "no" on a catch trial is not an error.
			fb = self.large_font.render("yes" if self.response_seen else "no", True, self.WHITE)
			center_text(fb, center_y)

		elif self.state == 'block_end':
			signal = [r for r in self.block_results if r['stimulus_present']]
			noise = [r for r in self.block_results if not r['stimulus_present']]
			last_n = signal[-10:] if len(signal) >= 10 else signal
			if last_n:
				key = 'duration_ms' if block == 'duration' else 'hue_offset'
				unit = 'ms' if block == 'duration' else 'offset units'
				thresh = sum(r[key] for r in last_n) / len(last_n)
				fa = sum(1 for r in noise if r['seen'])
				lines = [
					"Block complete!",
					f"Threshold: {thresh:.1f} {unit}",
					f"False alarms: {fa}/{len(noise)}",
					"Press SPACE to continue" if self.block_idx < len(self.blocks) - 1 else "Press SPACE to finish"
				]
				for i, line in enumerate(lines):
					t = self.font.render(line, True, self.WHITE)
					center_text(t, center_y - 60 + i * 45)


def run_brief_stimulus_detection(screen, font):
	test = BriefStimulusDetectionTest(screen, font)
	return test.run()

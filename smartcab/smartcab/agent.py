import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.qvals = {}
        self.time = 0
        self.discount_rate = 0.9

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.old_state, self.old_action = None, None
        self.old_reward = 0

    def best_action(self, state):
        """
        Returns the best action for the state,
        given as the action in the (state, action) tuple
        that yields the largest Q-value from self.qvals.
        If more than one action returns the same largest Q-value,
        one of these actions is chosen at random.
        """
        possible_actions = (None, 'left', 'forward', 'right')

        if random.random() < (1.0 / self.time):
            return random.choice(possible_actions)
                
        # get Q-values for each action given the state
        # (or 0 if (state, action) tuple not in self.qvals)
        action_qvals = {action: self.qvals.get((state, action), 0)
                        for action in possible_actions}        
        
        # select actions with maximum Q-values
        best_actions = [action for action in action_qvals
                        if action_qvals[action] == max(action_qvals.values())]
        
        # return one of the best actions at random
        return random.choice(best_actions)

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        
        # Increment t and get new learning rate
        self.time += 1
        learning_rate = 1.0 / self.time
        
        # Update state
        self.state = (inputs['light'], inputs['oncoming'], inputs['left'],
                      self.next_waypoint)

        # Pick the best action (as far as the agent knows)
        action = self.best_action(self.state)

        # Execute action and get reward
        reward = self.env.act(self, action)

        # Update the Q-value for the (state, action) tuple
        self.qvals[(self.old_state, self.old_action)] = \
            (1 - learning_rate) * \
                self.qvals.get((self.old_state, self.old_action), 0) + \
            learning_rate * \
                (self.old_reward + self.discount_rate * \
                    self.qvals.get((self.state, action), 0))
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]
        
        self.old_state = self.state
        self.old_action = action
        self.old_reward = reward

def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=0)  # reduce update_delay to speed up simulation
    sim.run(n_trials=100)  # press Esc or close pygame window to quit
    print a.qvals


if __name__ == '__main__':
    run()

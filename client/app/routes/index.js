import Route from '@ember/routing/route';
import { inject } from '@ember/service';

export default Route.extend(
  {
    session: inject(),
    beforeModel: function(transition) {
      if(!this.get('session.isAuthenticated')) {
        this.set('session.attemptedTransition', transition)
      }
    }
  }
);

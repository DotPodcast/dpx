import Controller from '@ember/controller';
import { inject } from '@ember/service';
import { computed } from '@ember/object';

export default Controller.extend(
  {
    session: inject(),
    pageWrapperClass: computed('session.isAuthenticated',
      function() {
        if(this.get('session.isAuthenticated')) {
          return 'page-wrapper'
        }

        return ''
      }
    ),
    actions: {
      logout() {
        this.get('session').invalidate();
      }
    }
  }
)

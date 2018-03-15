import Component from '@ember/component';
import { inject } from '@ember/service';

export default Component.extend(
  {
    tagName: 'ul',
    classNames: ['navbar-nav', 'ml-auto'],
    session: inject(),
    router: inject(),
    // toast: inject(),
    actions: {
      logout() {
        const session = this.get('session')
        const router = this.get('router')
        // const toast = this.get('toast')

        session.invalidate().then(
          () => {
            router.transitionTo('index')
            // toast.success('You have been logged out.')
          }
        )
      }
    }
  }
);

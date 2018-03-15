import Component from '@ember/component';
import { inject } from '@ember/service';

export default Component.extend(
  {
    session: inject(),
    classNames: ['dashboard-wrapper'],
    didInsertElement() {
      this.$('.side-menu').metisMenu()
    },
    actions: {
      logout() {
        this.get('session').invalidate()
      }
    }
  }
);

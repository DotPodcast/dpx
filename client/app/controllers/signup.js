import Controller from '@ember/controller';
import { inject } from '@ember/service';

export default Controller.extend(
  {
    session: inject(),
    // toast: inject(),
    actions: {
      submit() {
        this.get('model').save().then(
          () => {
            this.get('session').authenticate(
              'authenticator:django',
              this.get('model.username'),
              this.get('model.password')
            ).then(
              () => {
                // this.get('toast').success('You have been logged in. Welcome.')
              }
            )
          }
        )
      }
    }
  }
);

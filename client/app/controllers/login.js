import Controller from '@ember/controller';
import { inject } from '@ember/service';

export default Controller.extend(
  {
    session: inject(),
    // toast: inject(),
    actions: {
      authenticate() {
        const {
          username,
          password,
          remember
        } = this.getProperties(
          'username',
          'password'
        )

        const session = this.get('session')

        this.set('error', null)
        session.authenticate(
          'authenticator:django',
          username,
          password
        ).then(
          () => {
            // this.get('toast').success('You have been logged in.')
          }
        ).catch(
          err => {
            if(err && err.length) {
              this.set('error', err[0])
            }
          }
        )
      }
    }
  }
);

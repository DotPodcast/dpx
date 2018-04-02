import Controller from '@ember/controller';
import { inject } from '@ember/service';
import { computed } from '@ember/object';

export default Controller.extend(
  {
    importing: inject(),
    session: inject(),
    store: inject(),
    url: 'https://feeds.podiant.co/leopard/rss.xml',
    authRequired: false,
    submitting: computed(
      'userModel.{isSaving,isAuthenticating}',
      'importing.isImporting',
      function() {
        const saving = this.get('userModel.isSaving')
        const authenteicating = this.get('userModel.isAuthenticating')
        const importing = this.get('importing.isImporting')

        return saving || authenteicating || importing
      }
    ),
    init() {
      this._super(...arguments)
      this.set(
        'userModel',
        this.get('store').createRecord(
          'user',
          {
            username: 'foo',
            email: 'mark@steadman.io',
            password: 'barbarbar',
            passwordConfirmation: 'barbarbar'
          }
        )
      )
    },
    actions: {
      beginImportOrSignup() {
        if(!this.get('session.isAuthenticated')) {
          this.set('authRequired', true)
        } else {
          this.send('beginImport')
        }
      },
      beginImport() {
        this.get('importing').start(
          this.get('url')
        ).then(
          job => {
            this.transitionToRoute(
              'import-progress',
              {
                jobid: job.id
              }
            )
          }
        ).catch(
          xhr => {
            console.error(xhr)
          }
        )
      },
      signupAndBeginImport() {
        this.get('userModel').save().then(
          () => {
            this.set('userModel.isAuthenticating', true)
            this.get('session').authenticate(
              'authenticator:django',
              this.get('userModel.username'),
              this.get('userModel.password')
            ).then(
              () => {
                this.set('userModel.isAuthenticating', false)
                this.send('beginImport')
              },
              () => {
                this.set('userModel.isAuthenticating', false)
              }
            )
          }
        )
      }
    }
  }
);

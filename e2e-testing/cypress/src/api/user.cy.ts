import { login, registerUser } from '../support/user.util';

describe('@POST register user', () => {
  it('OK @201', () => {
    // Given
    const user = {
      username: `${Cypress.env('prefix')}${Date.now()}`,
      email: `${Cypress.env('prefix')}${Date.now()}@django-ninja.dev`,
      password: `${Cypress.env('prefix')}${Date.now()}`,
    };

    // When
    registerUser(user).then((response: Cypress.Response<User>) => {
      // Then
      expect(response.status).to.equal(201);
      expect(response.body.user.username).to.equal(user.username);
      expect(response.body.user.email).to.equal(user.email);
      expect(response.body.user).to.haveOwnProperty('token');
    });
  });

  it('KO @422 : empty username', () => {
    // Given
    const user = {
      username: '',
      email: `${Cypress.env('prefix')}${Date.now()}@django-ninja.dev`,
      password: `${Cypress.env('prefix')}${Date.now()}`,
    };

    // When
    registerUser(user).then((response: Cypress.Response<{ errors: { username: string[] } }>) => {
      // Then
      expect(response.status).to.equal(422);
      expect(response.body.detail[0].ctx.error).to.equal('can\'t be blank');
    });
  });

  it('KO @422 : empty email', () => {
    // Given
    const user = {
      username: `${Cypress.env('prefix')}${Date.now()}`,
      email: '',
      password: `${Cypress.env('prefix')}${Date.now()}`,
    };

    // When
    registerUser(user).then((response: Cypress.Response<{ errors: { email: string[] } }>) => {
      // Then
      expect(response.status).to.equal(422);  // error may depend from email lib
    });
  });

  it('KO @422 : empty password', () => {
    // Given
    const user = {
      username: `${Cypress.env('prefix')}${Date.now()}`,
      email: `${Cypress.env('prefix')}${Date.now()}@django-ninja.dev`,
      password: '',
    };

    // When
    registerUser(user).then((response: Cypress.Response<{ errors: { password: string[] } }>) => {
      // Then
      expect(response.status).to.equal(422);
      expect(response.body.detail[0].ctx.error).to.equal('can\'t be blank');
    });
  });

  it('KO @422 : existing credentials', () => {
    // Given
    const user = {
      username: `${Cypress.env('prefix')}${Date.now()}`,
      email: `${Cypress.env('prefix')}${Date.now()}@django-ninja.dev`,
      password: `${Cypress.env('prefix')}${Date.now()}`,
    };

    // When
    registerUser(user);
    registerUser(user).then(
      (response: Cypress.Response<{ errors: { username: string[]; email: string[] } }>) => {
        // Then
        expect(response.status).to.equal(409);
      },
    );
  });
});

describe('@POST login', () => {
  it('OK @200', () => {
    // Given
    const user = {
      username: `${Cypress.env('prefix')}${Date.now()}`,
      email: `${Cypress.env('prefix')}${Date.now()}@django-ninja.dev`,
      password: `${Cypress.env('prefix')}${Date.now()}`,
    };
    registerUser(user);

    // When
    login({
      email: user.email,
      password: user.password,
    }).then(response => {
      // Then
      expect(response.status).to.equal(200);
      expect(response.body.user.username).to.equal(user.username);
      expect(response.body.user.email).to.equal(user.email);
      expect(response.body.user).to.haveOwnProperty('token');
    });
  });

  it('KO @422 : empty email', () => {
    // Given
    const user = {
      username: `${Cypress.env('prefix')}${Date.now()}`,
      email: `${Cypress.env('prefix')}${Date.now()}@django-ninja.dev`,
      password: `${Cypress.env('prefix')}${Date.now()}`,
    };
    registerUser(user);

    // When
    login({
      email: '',
      password: user.password,
    }).then(response => {
      // Then
      expect(response.status).to.equal(422);
      expect(response.body.detail[0].ctx.error).to.equal('can\'t be blank');
    });
  });

  it('KO @422 : empty password', () => {
    // Given
    const user = {
      username: `${Cypress.env('prefix')}${Date.now()}`,
      email: `${Cypress.env('prefix')}${Date.now()}@django-ninja.dev`,
      password: `${Cypress.env('prefix')}${Date.now()}`,
    };
    registerUser(user);

    // When
    login({
      email: user.email,
      password: '',
    }).then(response => {
      // Then
      expect(response.status).to.equal(422);
      expect(response.body.detail[0].ctx.error).to.equal('can\'t be blank');
    });
  });

  it('KO @401 : incorrect password', () => {
    // Given
    const user = {
      username: `${Cypress.env('prefix')}${Date.now()}`,
      email: `${Cypress.env('prefix')}${Date.now()}@django-ninja.dev`,
      password: `${Cypress.env('prefix')}${Date.now()}`,
    };
    registerUser(user);

    // When
    login({
      email: user.email,
      password: 'incorrect',
    }).then(response => {
      // Then
      expect(response.status).to.equal(401);
      expect(response.body.detail[0].msg).to.equal('incorrect credentials');
    });
  });
});

// get current user
describe('@GET current user', () => {
  it('OK @200', () => {
    // Given
    const user = {
      username: `${Cypress.env('prefix')}${Date.now()}`,
      email: `${Cypress.env('prefix')}${Date.now()}@django-ninja.dev`,
      password: `${Cypress.env('prefix')}${Date.now()}`,
    };

    registerUser(user).then((response: Cypress.Response<User>) => {
      cy.wrap(response.body.user.token).as('token');
    });

    cy.then(function () {
      cy.getRequest('/api/user', this.token).then((response: Cypress.Response<User>) => {
        // Then
        expect(response.status).to.equal(200);
        expect(response.body.user.username).to.equal(user.username);
        expect(response.body.user.email).to.equal(user.email);
      });
    });
  });

  it('KO @401', () => {
    // When
    cy.getRequest('/api/user').then((response: Cypress.Response<{ message: string }>) => {
      // Then
      expect(response.status).to.equal(401);
    });
  });
});

// update user
describe('@PUT update user', () => {
  it('OK @200', () => {
    // Given
    const user = {
      username: `${Cypress.env('prefix')}${Date.now()}`,
      email: `${Cypress.env('prefix')}${Date.now()}@django-ninja.dev`,
      password: `${Cypress.env('prefix')}${Date.now()}`,
    };

    registerUser(user).then((response: Cypress.Response<User>) => {
      cy.wrap(response.body.user.token).as('token');
    });

    // When
    const updateUser = {
      username: `${Cypress.env('prefix')}${Date.now()}-2`,
      email: `${Cypress.env('prefix')}${Date.now()}-2@django-ninja.dev`,
    };
    cy.then(function () {
      cy.putRequest('/api/user', { user: updateUser }, this.token).then(
        (response: Cypress.Response<User>) => {
          // Then
          expect(response.status).to.equal(200);
          expect(response.body.user.username).to.equal(updateUser.username);
          expect(response.body.user.email).to.equal(updateUser.email);
          expect(response.body.user).to.haveOwnProperty('token');
          cy.wrap(response.body.user.token).as('token');
        },
      );
    });

    cy.then(function () {
      cy.getRequest('/api/user', this.token).then((response: Cypress.Response<User>) => {
        expect(response.status).to.equal(200);
        expect(response.body.user.username).to.equal(updateUser.username);
        expect(response.body.user.email).to.equal(updateUser.email);
      });
    });
  });

  it('KO @401', () => {
    // Given
    const user = {
      user: {
        username: `${Cypress.env('prefix')}${Date.now()}`,
        email: `${Cypress.env('prefix')}${Date.now()}@django-ninja.dev`,
      },
    };

    // When
    cy.putRequest('/api/user', { user })
      .as('userReponse')
      .then((response: Cypress.Response<{ message: string }>) => {
        // Then
        expect(response.status).to.equal(401);
      });
  });
});

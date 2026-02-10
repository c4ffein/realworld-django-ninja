export function registerUser(
  user: {
    username?: string;
    email?: string;
    password?: string;
  } = {
    username: `${Cypress.env('prefix')}${Date.now()}`,
    email: `${Cypress.env('prefix')}${Date.now()}@django-ninja.dev`,
    password: `${Cypress.env('prefix')}${Date.now()}`,
  },
): Cypress.Chainable {
  return cy.postRequest('/api/users', {
    user: {
        ...user,
        email: user.email.includes("@") ? user.email : `${user.email}@django-ninja.dev`,
    },
  });
}

export function login(user: { email?: string; password?: string }): Cypress.Chainable {
  return cy.postRequest('/api/users/login', {
    user,
  });
}

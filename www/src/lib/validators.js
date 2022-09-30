import { PASSWORD_STRENGTH } from "lib/constants"
import { isEmail } from "lib/utilities"

export const passwordStrengthValidator = (rule, value, callback) => {
  let strength = 0
  const { zxcvbn } = window

  if (value && zxcvbn) {
    const result = zxcvbn(value)
    strength = result.score
  }
  if (zxcvbn && strength < PASSWORD_STRENGTH) {
    callback("Password is not strong enough.")
  } else {
    callback()
  }
}

export const emailValidator = (rule, value, callback) => {
  if (typeof value === 'string' && isEmail(value) && value.length < 255) {
    callback();
  } else {
    callback("Email format is invalid.")
  }
  callback()
}

export const arrayOfEmailsValidator = (rule, value, callback) => {
  let violations = [];
  for (var i = 0; i < value.length; i++) {
    if (!isEmail(value[i])) {
      violations.push(value[i])
    }
  }

  if (violations.length > 0) {
    callback(`Email(s) are invalid: ${violations.join(', ')}`);
  } else {
    callback();
  }
}

import { login, logout, modifyUser } from '@/api/user'

const userStore = {
  namespaced: true,
  state: {
    isLogin: false,
    isLoginError: false,
    user: {},
    isValidToken: false
  },
  getter: {
    getUserInfo: function (state) {
      return state.user
    }
  },
  mutations: {
    SET_IS_LOGIN: (state, isLogin) => {
      state.isLogin = isLogin
    },
    SET_IS_LOGIN_ERROR: (state, isLoginError) => {
      state.isLoginError = isLoginError
    },
    SET_IS_VALID_TOKEN: (state, isValidToken) => {
      state.isValidToken = isValidToken
    },
    SET_USER_INFO: (state, user) => {
      state.isLogin = true
      state.user = user
      console.log(state.user)
    }
  },
  actions: {
    async userLogin ({ commit }, kakaoCode) {
      try {
        const data = await login(kakaoCode)
        if (data.statusText === 'OK') {
          let accessToken = data.headers['authorization']
          let refreshToken = data.headers['refresh']

          const user = {
            userId: data.data.userId,
            nickname: data.data.nickname,
            profileUrl: data.data.profileUrl
          }
          commit('SET_USER_INFO', user)
          commit('SET_IS_LOGIN', true)
          commit('SET_IS_LOGIN_ERROR', false)

          sessionStorage.setItem('accessToken', accessToken)
          sessionStorage.setItem('refreshToken', refreshToken)
          sessionStorage.setItem('isLoginUser', true)
          sessionStorage.setItem('userInfo', JSON.stringify(user))
          this.$router.push({ name: 'Main' })
        } else {
          commit('SET_IS_LOGIN', false)
          commit('SET_IS_LOGIN_ERROR', true)

          sessionStorage.setItem('isLoginUser', false)
        }
      } catch (error) {
        console.log(error)
      }
    },
    async userLogout ({ commit }) {
      try {
        const data = await logout()
        if (data.statusText === 'OK') {
          console.log(data)
          commit('SET_USER_INFO', null)
          commit('SET_IS_LOGIN', false)

          sessionStorage.removeItem('accessToken')
          sessionStorage.removeItem('refreshToken')
          sessionStorage.removeItem('userInfo')
          sessionStorage.removeItem('isLoginUser')

          this.$router.push({ name: 'Main' })
        } else {
          console.log('로그아웃 오류')
          commit('SET_IS_LOGIN', true)

          sessionStorage.setItem('isLoginUser', true)
        }
      } catch (error) {
        console.log(error)
      }
    },
    async userUpdate ({ commit }, formdata) {
      try {
        const data = await modifyUser(formdata)
        if (data.statusText === 'OK') {
          console.log(data.data.result)

          const userInfo = JSON.parse(sessionStorage.getItem('userInfo'))

          const user = {
            userId: userInfo.userId,
            nickname: data.data.result.nickname,
            profileUrl: data.data.result.profileUrl
          }
          console.log(user)
          commit('SET_USER_INFO', user)

          const updatedUserInfo = Object.assign(userInfo, user)
          console.log(updatedUserInfo)
          sessionStorage.setItem('userInfo', JSON.stringify(updatedUserInfo))
        } else {
          console.log('로그아웃 오류')
        }
      } catch (error) {
        console.log(error)
      }
    }

  }

}

export default userStore

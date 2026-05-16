// pages/start/start.js
Page({

  /**
   * 页面的初始数据
   */
  data: {

  },
GoToStudent(){
wx.navigateTo({
  url:'/pages/login/login?role=student',
  fail: (err) => {
      console.error('跳转失败原因:', err); // 查看控制台输出
      wx.showToast({ title: '跳转失败，看控制台', icon: 'none' });
    }
})
},
GoToAdmin(){
  wx.navigateTo({
    url:'/pages/login/login?role=admin',
    fail: (err) => {
      console.error('跳转失败原因:', err); // 查看控制台输出
      wx.showToast({ title: '跳转失败，看控制台', icon: 'none' });
    }
  })
  },
  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {

  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  }
})
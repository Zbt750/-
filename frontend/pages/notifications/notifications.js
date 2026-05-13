// pages/notifications/notifications.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    notifications: [],
    loading: true
  },
  // 获取通知
  fetchNotifications(){
  const token=wx.getStorageSync('token')
  if(!token){
    wx.redirectTo({ url: '/pages/login/login' });
      return;
  }
 wx.request({
  url:'http://127.0.0.1:8000/duty/notifications',
  method:'GET',
  header: { 'Authorization': `Bearer ${token}` },
  success:(res)=>{
    if(res.statusCode==200){
     this.setData({
      notifications:res.data.notifications,
      loading:false
     })
    }
    else{
      wx.showToast({ title: '获取失败', icon: 'none' });
          this.setData({ loading: false });
    }
  },
  fail: () => {
    wx.showToast({ title: '网络错误', icon: 'none' });
    this.setData({ loading: false });
  }
 })
  
  },
// 标记为已读通知
markRead(e){
  console.log('markRead 被触发')
  const id = e.currentTarget.dataset.id;
  console.log('通知ID：', id);
  const token = wx.getStorageSync('token');
  wx.request({
    url: `http://127.0.0.1:8000/duty/notifications/read?notification_id=${id}`,
    method:'POST',
    header: { 'Authorization': `Bearer ${token}` },
    success:(res)=>{
      console.log('标记已读返回：', res);
      if(res.statusCode==200){
        // 刷新一下通知
        console.log('标记已读成功');
        this.fetchNotifications()
      }
    },
    fail: (err) => {
      console.log('请求失败：', err);           
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
    console.log('通知页面 onShow 执行了，当前通知数量：', this.data.notifications.length);
  this.fetchNotifications();
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
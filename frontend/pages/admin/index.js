// pages/admin/index.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
   tasks:[],
   loading:true,
  },
  // 获取任务
fetchTasks(){
const token=wx.getStorageSync('token');
if (!token){
  wx.reLaunch({
    url: '/pages/login/login'
  });
  return
}
wx.request({
  url:'http://127.0.0.1:8000/admin/get_admin_tasks',
  method:'GET',
  header:{'Authorization': `Bearer ${token}`},
  success:(res)=>{
   if(res.statusCode==200)
   {
    this.setData({tasks:res.data.tasks,loading:false})
   }
   else if(res.statusCode === 401)
   {
    wx.removeStorageSync('token');
    wx.redirectTo({ url: '/pages/login/login' });
   }
   else{
   wx.showToast({title:'获取失败',icon:'none'});
   this.setData({ loading: false });
   }
  },
  fail: () => {
    wx.showToast({ title: '网络错误', icon: 'none' });
    this.setData({ loading: false });
  },
})
},
// 后端返回的数据，被前端代码接收并存在了 data 里。这里用e接收
goEvaluate(e) {
  const recordId = e.currentTarget.dataset.id;
  wx.navigateTo({ url: `/pages/admin/evaluate?recordId=${recordId}` });
},

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
   this.fetchTasks();
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
    console.log('onShow 执行了');
    if (!this.data.loading) {
      this.fetchTasks();
    }
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
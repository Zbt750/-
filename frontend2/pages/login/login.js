
// pages/login/login.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
  student_id:'',
  name:'',
  role:'student'
  },
  onStudentInput(e){
    this.setData({
      student_id:e.detail.value
    });
  },
  onNameInput(e){
    this.setData({
      name:e.detail.value
    });
  },
  onLogin(){
    const{student_id,name,role}=this.data;
    if(!student_id || !name){
      wx.showToast({title:'请输入完整信息' , icon:'none'})
      return 
     }
    wx.request({
      url:'http://121.41.20.177:8000/auth/login',
      method:'POST',
      data:{student_id,name},
      header:{
        'Content-Type':'application/json'
      },
      success:(res)=>{
        const data=res.data
        if (res.statusCode==200)
        {
          
          wx.setStorageSync('token', data.access_token);
          wx.setStorageSync('user_id',data.user_id);
          wx.setStorageSync('class_id',data.class_id);
          wx.setStorageSync('name', name); 
          wx.setStorageSync('is_admin', data.is_admin)
          const is_admin = data.is_admin;
          if (role=='admin'&&!is_admin){
            wx.showToast({title:'您不是管理员',icon:'none'})
            return
          }
          if(role=='student'&&is_admin){
            //
          }
          if(role=='admin'&&is_admin){
            wx.reLaunch({url:'/pages/admin/index'})
          }
          else{
            wx.reLaunch({ url: '/pages/index/index' });
          }
        }
        else{
          wx.showToast({title:res.data.detail || '登录失败',icon:'none'})
        };
      },
      fail:()=>{
        wx.showToast({title:'网络错误',icon:'none'})
      }
    })
      
  },


  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    if (options.role) {
      this.setData({ role: options.role });
    }
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